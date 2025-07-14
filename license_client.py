import hashlib
import platform
import uuid
import aiohttp
import asyncio
import json
from datetime import datetime

class LicenseClient:
    def __init__(self, server_url="http://127.0.0.1:8080"):
        # Cambiar aquí la URL del servidor a la URL pública de ngrok
        self.server_url = "https://be389ed3e5cf.ngrok-free.app"
        self.hardware_id = self._get_hardware_id()
        self.user_data = None
        self.session = None
    
    def _get_hardware_id(self):
        """Genera un ID único basado en el hardware del sistema"""
        # Combinar información del sistema para crear un ID único
        system_info = f"{platform.node()}-{platform.processor()}-{platform.system()}"
        
        # Intentar obtener MAC address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            system_info += f"-{mac}"
        except:
            pass
        
        # Crear hash SHA256
        hardware_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
        return hardware_id
    
    async def _make_request(self, endpoint, data=None, method='POST'):
        """Realiza una petición HTTP al servidor"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.server_url}{endpoint}"
            
            if method == 'POST':
                async with self.session.post(url, json=data, timeout=10) as response:
                    return response.status, await response.json()
            else:
                async with self.session.get(url, timeout=10) as response:
                    return response.status, await response.json()
                    
        except aiohttp.ClientError as e:
            return None, {'error': f'Error de conexión: {e}'}
        except asyncio.TimeoutError:
            return None, {'error': 'Timeout: El servidor no responde'}
        except Exception as e:
            return None, {'error': f'Error inesperado: {e}'}
    
    async def validate_license(self, groups_count=0, cards_to_send=0):
        """Valida la licencia del usuario"""
        data = {
            'hardware_id': self.hardware_id,
            'groups_count': groups_count,
            'cards_to_send': cards_to_send
        }
        
        status, response = await self._make_request('/api/validate', data)
        
        if status is None:
            return False, response.get('error', 'Error de conexión'), None
        
        if status == 200:
            self.user_data = response.get('user')
            return True, response.get('message', 'Licencia válida'), self.user_data
        else:
            return False, response.get('error', 'Licencia inválida'), None
    
    async def activate_premium(self, activation_code):
        """Activa el plan premium con un código"""
        data = {
            'hardware_id': self.hardware_id,
            'activation_code': activation_code.strip().upper()
        }
        
        status, response = await self._make_request('/api/activate', data)
        
        if status is None:
            return False, response.get('error', 'Error de conexión')
        
        success = response.get('success', False)
        message = response.get('message', 'Error desconocido')
        
        return success, message
    
    async def update_usage(self, groups_used, cards_sent):
        """Actualiza el uso del usuario en el servidor"""
        data = {
            'hardware_id': self.hardware_id,
            'groups_used': groups_used,
            'cards_sent': cards_sent
        }
        
        status, response = await self._make_request('/api/usage', data)
        
        if status == 200:
            return True, 'Uso actualizado correctamente'
        else:
            return False, response.get('error', 'Error actualizando uso')
    
    async def check_server_connection(self):
        """Verifica si el servidor está disponible"""
        status, response = await self._make_request('/health', method='GET')
        
        if status == 200:
            return True, 'Servidor disponible'
        else:
            return False, response.get('error', 'Servidor no disponible')
    
    def get_user_info(self):
        """Obtiene información del usuario actual"""
        return {
            'hardware_id': self.hardware_id,
            'user_data': self.user_data
        }
    
    def display_user_info(self):
        """Muestra información del usuario de forma amigable"""
        if not self.user_data:
            print("❌ No hay información de usuario disponible")
            return
        
        plan = self.user_data.get('plan', 'unknown')
        plan_emoji = "⭐" if plan == 'premium' else "🆓"
        
        print(f"\n👤 INFORMACIÓN DEL USUARIO")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🆔 ID de Usuario: {self.user_data.get('id', 'N/A')}")
        print(f"💻 Hardware ID: {self.hardware_id[:8]}...")
        print(f"{plan_emoji} Plan: {plan.upper()}")
        print(f"📅 Registrado: {self.user_data.get('created_at', 'N/A')[:10]}")
        print(f"🕒 Última actividad: {self.user_data.get('last_active', 'N/A')[:16]}")
        print(f"📊 Grupos usados: {self.user_data.get('groups_used', 0)}")
        print(f"💳 Tarjetas hoy: {self.user_data.get('cards_sent_today', 0)}")
        print(f"📈 Total tarjetas: {self.user_data.get('total_cards_sent', 0)}")
        
        if plan == 'free':
            remaining_cards = 20 - self.user_data.get('cards_sent_today', 0)
            print(f"⚠️  Límites FREE: 5 grupos máx, {remaining_cards} tarjetas restantes hoy")
        else:
            print(f"✅ Plan PREMIUM: Sin límites")
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    def display_plan_limits(self):
        """Muestra los límites de cada plan"""
        print("\n📋 PLANES DISPONIBLES")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🆓 PLAN FREE:")
        print("   • Máximo 5 grupos")
        print("   • Máximo 20 tarjetas por día")
        print("   • Funciones básicas")
        print()
        print("⭐ PLAN PREMIUM:")
        print("   • Grupos ilimitados")
        print("   • Tarjetas ilimitadas")
        print("   • Todas las funciones")
        print("   • Soporte prioritario")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    async def interactive_activation(self):
        """Proceso interactivo para activar premium"""
        print("\n🎫 ACTIVACIÓN DE PLAN PREMIUM")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        activation_code = input("Ingresa tu código de activación: ").strip()
        
        if not activation_code:
            print("❌ Código de activación requerido")
            return False
        
        print("🔄 Validando código...")
        
        success, message = await self.activate_premium(activation_code)
        
        if success:
            print(f"✅ {message}")
            print("🎉 ¡Felicidades! Ahora tienes acceso premium")
            
            # Revalidar licencia para obtener datos actualizados
            await self.validate_license()
            return True
        else:
            print(f"❌ {message}")
            return False
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

# Función de utilidad para usar en otros scripts
async def check_license_and_limits(groups_count, cards_to_send):
    """
    Función de utilidad para validar licencia y límites
    Retorna: (puede_continuar, mensaje, datos_usuario)
    """
    client = LicenseClient()
    
    try:
        # Verificar conexión al servidor
        server_ok, server_msg = await client.check_server_connection()
        if not server_ok:
            return False, f"❌ SERVIDOR DE LICENCIAS NO DISPONIBLE\n   {server_msg}\n   El script no puede ejecutarse sin conexión al servidor.", None
        
        # Validar licencia
        valid, message, user_data = await client.validate_license(groups_count, cards_to_send)
        
        if valid:
            client.display_user_info()
            return True, message, user_data
        else:
            client.display_user_info()
            client.display_plan_limits()
            
            # Si es problema de límites, ofrecer activación premium
            if "limitado" in message.lower():
                print(f"❌ {message}")
                print("\n💡 ¿Quieres activar el plan PREMIUM para eliminar estas limitaciones?")
                choice = input("¿Tienes un código de activación? (s/n): ").strip().lower()
                
                if choice == 's':
                    if await client.interactive_activation():
                        # Revalidar después de la activación
                        valid, message, user_data = await client.validate_license(groups_count, cards_to_send)
                        if valid:
                            client.display_user_info()
                            return True, message, user_data
            
            return False, message, user_data
    
    finally:
        await client.close()

# Función para actualizar uso después de enviar tarjetas
async def update_usage_stats(groups_used, cards_sent):
    """
    Actualiza las estadísticas de uso en el servidor
    """
    client = LicenseClient()
    
    try:
        success, message = await client.update_usage(groups_used, cards_sent)
        if success:
            print(f"📊 Estadísticas actualizadas: {cards_sent} tarjetas enviadas a {groups_used} grupos")
        else:
            print(f"⚠️  No se pudieron actualizar las estadísticas: {message}")
    except Exception as e:
        print(f"⚠️  Error actualizando estadísticas: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    # Ejemplo de uso
    async def test_client():
        client = LicenseClient()
        
        print("🔍 Verificando conexión al servidor...")
        server_ok, msg = await client.check_server_connection()
        print(f"Servidor: {msg}")
        
        if server_ok:
            print("\n🔍 Validando licencia...")
            valid, message, user_data = await client.validate_license(3, 10)
            print(f"Licencia: {message}")
            
            if valid:
                client.display_user_info()
            else:
                client.display_plan_limits()
        
        await client.close()
    
    asyncio.run(test_client())
