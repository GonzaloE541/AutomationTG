import os
import json
import asyncio
from pyrogram import Client, filters, errors
from dotenv import load_dotenv
from license_client import check_license_and_limits, update_usage_stats

# Cargar variables de entorno
load_dotenv()

STATE_FILE = "send_state.json"
PREFIX_FILE = "prefix_state.json"
WAIT_TIME = 40  # Tiempo de espera en segundos antes de reenviar mensajes

def get_env_value(key):
    """Obtiene un valor del archivo .env de forma segura"""
    value = os.getenv(key)
    return value if value else None

def save_to_env(key, value):
    """Guarda o actualiza un valor en el archivo .env"""
    env_file = ".env"
    
    # Leer contenido actual del .env
    env_content = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_content[k.strip()] = v.strip()
    
    # Actualizar el valor
    env_content[key] = str(value)
    
    # Escribir de vuelta al archivo
    with open(env_file, 'w') as f:
        for k, v in env_content.items():
            f.write(f"{k}={v}\n")
    
    # Recargar variables de entorno
    load_dotenv(override=True)

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime el header del programa"""
    print("🚀 TELEGRAM AUTOMATION - CARD SENDER")
    print("=" * 50)
    print()

def check_initial_setup():
    """Verifica si es la primera vez que se ejecuta el programa"""
    api_id = get_env_value("API_ID")
    api_hash = get_env_value("API_HASH")
    
    return api_id is None or api_hash is None

async def initial_setup():
    """Configuración inicial para nuevos usuarios"""
    clear_screen()
    print_header()
    print("🎉 ¡BIENVENIDO AL SISTEMA DE AUTOMATIZACIÓN!")
    print("=" * 50)
    print()
    print("Parece que es tu primera vez usando este programa.")
    print("Necesitamos configurar algunos datos básicos para comenzar.")
    print()
    print("📋 INFORMACIÓN REQUERIDA:")
    print("1. API_ID y API_HASH de Telegram")
    print("2. Grupos donde enviar las tarjetas")
    print("3. Grupo privado para recibir respuestas")
    print()
    
    input("Presiona Enter para continuar con la configuración...")
    
    # Configurar API_ID y API_HASH
    clear_screen()
    print_header()
    print("🔑 CONFIGURACIÓN DE API DE TELEGRAM")
    print("=" * 40)
    print()
    print("Para obtener tu API_ID y API_HASH:")
    print("1. Ve a https://my.telegram.org/apps")
    print("2. Inicia sesión con tu número de teléfono")
    print("3. Crea una nueva aplicación")
    print("4. Copia el API_ID y API_HASH")
    print()
    
    while True:
        try:
            api_id = input("Ingresa tu API_ID: ").strip()
            if not api_id:
                print("❌ API_ID no puede estar vacío")
                continue
            
            # Verificar que sea numérico
            int(api_id)
            break
        except ValueError:
            print("❌ API_ID debe ser un número")
    
    while True:
        api_hash = input("Ingresa tu API_HASH: ").strip()
        if not api_hash:
            print("❌ API_HASH no puede estar vacío")
            continue
        break
    
    # Guardar API credentials
    save_to_env("API_ID", api_id)
    save_to_env("API_HASH", api_hash)
    
    print("\n✅ Credenciales de API guardadas correctamente")
    
    # Configurar grupos
    await setup_groups()
    
    print("\n🎉 ¡CONFIGURACIÓN INICIAL COMPLETADA!")
    print("Ahora puedes usar el programa normalmente.")
    input("\nPresiona Enter para continuar...")

async def setup_groups():
    """Configuración de grupos"""
    clear_screen()
    print_header()
    print("📱 CONFIGURACIÓN DE GRUPOS")
    print("=" * 40)
    print()
    print("Ahora vamos a configurar los grupos donde se enviarán las tarjetas.")
    print()
    print("💡 TIPOS DE IDENTIFICADORES VÁLIDOS:")
    print("   • Username: @migrupo")
    print("   • ID numérico: -1001234567890")
    print("   • Puedes usar el script 'find_group_id.py' para encontrar IDs")
    print()
    
    groups_list = []
    
    while True:
        print(f"\n📋 GRUPOS CONFIGURADOS ({len(groups_list)}):")
        if groups_list:
            for i, group in enumerate(groups_list, 1):
                print(f"   {i}. {group}")
        else:
            print("   (Ninguno)")
        
        print("\n🔧 OPCIONES:")
        print("1. ➕ Agregar grupo")
        print("2. ❌ Eliminar grupo")
        print("3. ✅ Finalizar configuración")
        
        choice = input("\nSelecciona una opción (1-3): ").strip()
        
        if choice == "1":
            group = input("\nIngresa el ID o username del grupo: ").strip()
            if group:
                if group not in groups_list:
                    groups_list.append(group)
                    print(f"✅ Grupo '{group}' agregado")
                else:
                    print("⚠️  Este grupo ya está en la lista")
            else:
                print("❌ No puedes agregar un grupo vacío")
        
        elif choice == "2":
            if groups_list:
                print("\n📋 GRUPOS PARA ELIMINAR:")
                for i, group in enumerate(groups_list, 1):
                    print(f"   {i}. {group}")
                
                try:
                    index = int(input("\nNúmero del grupo a eliminar: ")) - 1
                    if 0 <= index < len(groups_list):
                        removed = groups_list.pop(index)
                        print(f"✅ Grupo '{removed}' eliminado")
                    else:
                        print("❌ Número inválido")
                except ValueError:
                    print("❌ Ingresa un número válido")
            else:
                print("⚠️  No hay grupos para eliminar")
        
        elif choice == "3":
            if len(groups_list) == 0:
                print("❌ Debes agregar al menos un grupo")
                continue
            break
        
        else:
            print("❌ Opción inválida")
    
    # Guardar grupos
    groups_str = ",".join(groups_list)
    save_to_env("GROUPS", groups_str)
    
    # Configurar grupo privado
    print("\n🔒 GRUPO PRIVADO PARA RESPUESTAS")
    print("-" * 30)
    print("Este es el grupo donde recibirás las respuestas de los bots.")
    
    while True:
        private_group = input("Ingresa el ID o username del grupo privado: ").strip()
        if private_group:
            save_to_env("PRIVATE_GROUP", private_group)
            print(f"✅ Grupo privado '{private_group}' configurado")
            break
        else:
            print("❌ El grupo privado no puede estar vacío")

async def show_main_menu():
    """Muestra el menú principal"""
    while True:
        clear_screen()
        print_header()
        
        # Mostrar información actual
        api_id = get_env_value("API_ID")
        groups = get_env_value("GROUPS")
        private_group = get_env_value("PRIVATE_GROUP")
        
        # Mostrar versión del plan
        plan_version = "Desconocido"
        try:
            import asyncio
            from license_client import LicenseClient
            client = LicenseClient()
            loop = asyncio.get_event_loop()
            valid, message, user_data = loop.run_until_complete(client.validate_license(len(groups.split(',')) if groups else 0, 0))
            if valid and user_data and user_data.get('plan'):
                plan_version = user_data['plan'].capitalize()
        except Exception:
            plan_version = "Desconocido"
        
        print(f"📊 CONFIGURACIÓN ACTUAL - Plan: {plan_version}")
        print(f"   🔑 API_ID: {'✅ Configurado' if api_id else '❌ No configurado'}")
        print(f"   📱 Grupos: {len(groups.split(',')) if groups else 0} configurados")
        print(f"   🔒 Grupo privado: {'✅ Configurado' if private_group else '❌ No configurado'}")
        print()
        
        print("📋 MENÚ PRINCIPAL:")
        print("1. 🚀 Iniciar envío de tarjetas")
        print("2. ⚙️  Configurar API de Telegram")
        print("3. 📱 Gestionar grupos")
        print("4. 🔒 Configurar grupo privado")
        print("5. 🎫 Activar código premium")
        print("6. 📊 Ver configuración actual")
        print("7. ❌ Salir")
        print()
        
        choice = input("Selecciona una opción (1-7): ").strip()
        
        if choice == "1":
            if api_id and groups and private_group:
                await start_card_sending()
            else:
                print("\n❌ CONFIGURACIÓN INCOMPLETA")
                print("Debes configurar API_ID, grupos y grupo privado antes de continuar.")
                input("Presiona Enter para continuar...")
        
        elif choice == "2":
            await configure_api()
        
        elif choice == "3":
            await manage_groups()
        
        elif choice == "4":
            await configure_private_group()
        
        elif choice == "5":
            await activate_premium_code()
        
        elif choice == "6":
            await show_current_config()
        
        elif choice == "7":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción inválida")
            input("Presiona Enter para continuar...")

async def configure_api():
    """Configurar API de Telegram"""
    clear_screen()
    print_header()
    print("🔑 CONFIGURACIÓN DE API DE TELEGRAM")
    print("=" * 40)
    
    current_api_id = get_env_value("API_ID")
    current_api_hash = get_env_value("API_HASH")
    
    if current_api_id and current_api_hash:
        print(f"📊 CONFIGURACIÓN ACTUAL:")
        print(f"   API_ID: {current_api_id}")
        print(f"   API_HASH: {current_api_hash[:8]}...")
        print()
        
        change = input("¿Quieres cambiar la configuración actual? (s/n): ").strip().lower()
        if change != 's':
            return
    
    print("\n🔧 NUEVA CONFIGURACIÓN:")
    print("Para obtener tu API_ID y API_HASH:")
    print("1. Ve a https://my.telegram.org/apps")
    print("2. Inicia sesión con tu número de teléfono")
    print("3. Crea una nueva aplicación")
    print("4. Copia el API_ID y API_HASH")
    print()
    
    while True:
        try:
            api_id = input("Nuevo API_ID: ").strip()
            if not api_id:
                print("❌ API_ID no puede estar vacío")
                continue
            int(api_id)
            break
        except ValueError:
            print("❌ API_ID debe ser un número")
    
    while True:
        api_hash = input("Nuevo API_HASH: ").strip()
        if not api_hash:
            print("❌ API_HASH no puede estar vacío")
            continue
        break
    
    save_to_env("API_ID", api_id)
    save_to_env("API_HASH", api_hash)
    
    print("\n✅ Configuración de API actualizada correctamente")
    input("Presiona Enter para continuar...")

async def manage_groups():
    """Gestionar grupos"""
    await setup_groups()

async def configure_private_group():
    """Configurar grupo privado"""
    clear_screen()
    print_header()
    print("🔒 CONFIGURACIÓN DE GRUPO PRIVADO")
    print("=" * 40)
    
    current_private = get_env_value("PRIVATE_GROUP")
    
    if current_private:
        print(f"📊 GRUPO PRIVADO ACTUAL: {current_private}")
        print()
        
        change = input("¿Quieres cambiar el grupo privado? (s/n): ").strip().lower()
        if change != 's':
            return
    
    print("\n🔧 NUEVO GRUPO PRIVADO:")
    print("Este es el grupo donde recibirás las respuestas de los bots.")
    print()
    
    while True:
        private_group = input("Ingresa el ID o username del grupo privado: ").strip()
        if private_group:
            save_to_env("PRIVATE_GROUP", private_group)
            print(f"\n✅ Grupo privado '{private_group}' configurado correctamente")
            break
        else:
            print("❌ El grupo privado no puede estar vacío")
    
    input("Presiona Enter para continuar...")

async def show_current_config():
    """Mostrar configuración actual"""
    clear_screen()
    print_header()
    print("📊 CONFIGURACIÓN ACTUAL DEL SISTEMA")
    print("=" * 50)
    
    api_id = get_env_value("API_ID")
    api_hash = get_env_value("API_HASH")
    groups = get_env_value("GROUPS")
    private_group = get_env_value("PRIVATE_GROUP")
    
    print("🔑 API DE TELEGRAM:")
    if api_id and api_hash:
        print(f"   ✅ API_ID: {api_id}")
        print(f"   ✅ API_HASH: {api_hash[:8]}...")
    else:
        print("   ❌ No configurado")
    
    print("\n📱 GRUPOS CONFIGURADOS:")
    if groups:
        group_list = [g.strip() for g in groups.split(",") if g.strip()]
        for i, group in enumerate(group_list, 1):
            print(f"   {i}. {group}")
        print(f"\n   Total: {len(group_list)} grupos")
    else:
        print("   ❌ No hay grupos configurados")
    
    print("\n🔒 GRUPO PRIVADO:")
    if private_group:
        print(f"   ✅ {private_group}")
    else:
        print("   ❌ No configurado")
    
    print("\n📁 ARCHIVOS:")
    print(f"   📄 cards.txt: {'✅ Existe' if os.path.exists('cards.txt') else '❌ No encontrado'}")
    print(f"   ⚙️  .env: {'✅ Existe' if os.path.exists('.env') else '❌ No encontrado'}")
    
    input("\nPresiona Enter para continuar...")

async def activate_premium_code():
    """Permite al usuario ingresar un código premium para activar el plan"""
    clear_screen()
    print_header()
    print("🎫 ACTIVAR PLAN PREMIUM")
    print("=" * 40)
    print()
    
    code = input("Ingresa tu código de activación premium: ").strip()
    if not code:
        print("❌ Código vacío. Operación cancelada.")
        input("Presiona Enter para continuar...")
        return
    
    try:
        from license_client import LicenseClient
        client = LicenseClient()
        success, message = await client.activate_premium(code)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    except Exception as e:
        print(f"❌ Error al activar código: {e}")
    
    input("Presiona Enter para continuar...")

# Funciones originales del programa
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_prefixes():
    if os.path.exists(PREFIX_FILE):
        with open(PREFIX_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prefixes(prefixes):
    with open(PREFIX_FILE, "w") as f:
        json.dump(prefixes, f)

async def send_message_to_group(app, group, message):
    """Envía un mensaje al grupo o usuario especificado."""
    try:
        sent_msg = await app.send_message(group, message)
        print(f"Mensaje enviado a {group}: {message}")
        return sent_msg
    except Exception as e:
        print(f"Error enviando mensaje a {group}: {e}")
        return None

def read_cards_from_file():
    """Lee las tarjetas desde el archivo cards.txt"""
    try:
        with open("cards.txt", "r") as file:
            cards = [line.strip() for line in file.readlines() if line.strip()]
        print(f"\nSe detectaron {len(cards)} tarjetas en el archivo cards.txt")
        return cards
    except FileNotFoundError:
        print("Error: No se encontró el archivo cards.txt")
        return []

def cleanup_state():
    """Elimina el archivo de estado de envíos"""
    if os.path.exists(STATE_FILE):
        try:
            os.remove(STATE_FILE)
            print("\nRegistro de envíos eliminado correctamente.")
        except Exception as e:
            print(f"\nError al eliminar registro de envíos: {e}")

async def resolve_chat(app, chat_id):
    """Resuelve un chat_id a un objeto de chat"""
    try:
        chat = await app.get_chat(chat_id)
        return chat
    except errors.RPCError:
        return None

async def forward_messages_safely(app, messages, private_group):
    """Reenvía mensajes de forma segura al grupo privado"""
    try:
        # Intentar resolver el grupo privado primero
        target_chat = await resolve_chat(app, private_group)
        if not target_chat:
            print(f"Error: No se pudo acceder al grupo privado {private_group}")
            return False

        for msg in messages:
            try:
                await asyncio.sleep(1)  # Pequeña pausa entre reenvíos
                await msg.forward(target_chat.id)
            except errors.RPCError as e:
                print(f"Error reenviando mensaje: {e}")
                continue
        return True
    except Exception as e:
        print(f"Error en forward_messages_safely: {e}")
        return False

async def start_card_sending():
    """Inicia el proceso de envío de tarjetas (función principal original)"""
    clear_screen()
    print_header()
    print("🚀 INICIANDO ENVÍO DE TARJETAS...")
    print("=" * 40)
    
    # Obtener valores actuales del .env
    api_id = int(get_env_value("API_ID"))
    api_hash = get_env_value("API_HASH")
    groups = get_env_value("GROUPS")
    private_group = get_env_value("PRIVATE_GROUP")
    
    # Obtener lista de grupos/usuarios (IDs o usernames)
    group_list_raw = [g.strip() for g in groups.split(",") if g.strip()]
    group_list = []
    for g in group_list_raw:
        # Intentar convertir a entero para IDs numéricos, si falla dejar como string
        try:
            group_list.append(int(g))
        except ValueError:
            group_list.append(g)

    # Cargar prefijos guardados
    saved_prefixes = load_prefixes()
    prefix_map = {}

    # Resolver nombres de grupos para mostrar junto con IDs
    resolved_names = {}
    async with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
        for group in group_list_raw:
            try:
                chat = await app.get_chat(group)
                resolved_names[str(group)] = chat.title or chat.first_name or "Sin nombre"
            except Exception:
                resolved_names[str(group)] = "Nombre no disponible"

    # Preguntar si quiere cambiar prefijos
    if saved_prefixes:
        print("\nPrefijos guardados:")
        for group in group_list_raw:
            saved_prefix = saved_prefixes.get(str(group), "")
            name = resolved_names.get(str(group), "Nombre no disponible")
            print(f"{group} - {name}: {saved_prefix}")
        
        change = input("\n¿Quieres cambiar los prefijos? (s/n): ").strip().lower()
        if change == 's':
            print("\nIngresa los nuevos prefijos (deja vacío para mantener el actual):")
            for group in group_list_raw:
                current = saved_prefixes.get(str(group), "")
                name = resolved_names.get(str(group), "Nombre no disponible")
                prefix = input(f"Nuevo prefijo para {group} - {name} [{current}]: ").strip()
                prefix_map[str(group)] = prefix if prefix else current
            # Guardar nuevos prefijos
            save_prefixes(prefix_map)
            print("Nuevos prefijos guardados correctamente.")
        else:
            prefix_map = saved_prefixes
    else:
        print("\nConfigura los prefijos para cada grupo/usuario:")
        for group in group_list_raw:
            name = resolved_names.get(str(group), "Nombre no disponible")
            prefix = input(f"¿Qué prefijo quieres usar para {group} - {name}? (ejemplo: .au): ").strip()
            prefix_map[str(group)] = prefix
        # Guardar prefijos por primera vez
        save_prefixes(prefix_map)
        print("Prefijos guardados correctamente.")

    # Leer tarjetas
    cards = read_cards_from_file()
    if not cards:
        input("Presiona Enter para volver al menú...")
        return

    print(f"\n🔐 VERIFICANDO LICENCIA Y LÍMITES...")
    print("-" * 40)
    
    # VALIDACIÓN DE LICENCIA - NUEVA FUNCIONALIDAD
    can_proceed, license_message, user_data = await check_license_and_limits(
        groups_count=len(group_list),
        cards_to_send=len(cards)
    )
    
    if not can_proceed:
        print(f"\n❌ NO SE PUEDE CONTINUAR:")
        print(f"   {license_message}")
        print("\n💡 Contacta al administrador para obtener acceso premium")
        input("Presiona Enter para volver al menú...")
        return
    
    print(f"✅ {license_message}")
    
    # Cargar estado de envíos previos
    state = load_state()
    
    # Inicializar estado para grupos que no existan
    for group in group_list:
        key = str(group)
        if key not in state:
            state[key] = []

    # Iniciar cliente de Telegram
    app = Client("my_account", api_id=api_id, api_hash=api_hash)

    # Diccionario para rastrear los últimos mensajes enviados y sus respuestas
    last_sent_messages = {}
    message_responses = {}
    processing_chats = set()

    @app.on_message(filters.chat(group_list))
    async def forward_responses(client, message):
        try:
            chat_id = str(message.chat.id)
            
            # Si es una respuesta a uno de nuestros mensajes o un mensaje de bot
            if (message.reply_to_message and message.reply_to_message.id in last_sent_messages.values()) or \
               (message.from_user and message.from_user.is_bot):
                
                # Si el chat no está siendo procesado, iniciar nuevo proceso
                if chat_id not in processing_chats:
                    processing_chats.add(chat_id)
                    
                    # Inicializar o limpiar lista de mensajes para este chat
                    message_responses[chat_id] = []
                    
                    # Programar el reenvío después de WAIT_TIME segundos
                    async def process_messages():
                        try:
                            # Esperar WAIT_TIME segundos
                            await asyncio.sleep(WAIT_TIME)
                            
                            # Reenviar mensajes acumulados
                            if chat_id in message_responses and message_responses[chat_id]:
                                print(f"\nReenviando mensajes del chat {message.chat.title} después de {WAIT_TIME} segundos")
                                await forward_messages_safely(client, message_responses[chat_id], private_group)
                                # Limpiar mensajes enviados
                                message_responses[chat_id] = []
                        
                        finally:
                            # Remover chat de procesamiento
                            processing_chats.discard(chat_id)
                    
                    # Iniciar tarea de procesamiento
                    asyncio.create_task(process_messages())
                
                # Añadir mensaje a la lista de respuestas
                if chat_id in message_responses:
                    message_responses[chat_id].append(message)
                
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            processing_chats.discard(chat_id)

    try:
        # Iniciar sesión
        await app.start()
        
        # Verificar sesión y grupos
        try:
            me = await app.get_me()
            print(f"\nUsando sesión existente para: {me.first_name}")
            
            # Verificar acceso a grupos
            print("\nVerificando acceso a grupos...")
            for group in group_list:
                chat = await resolve_chat(app, group)
                if chat:
                    print(f"✓ Acceso confirmado a: {chat.title}")
                else:
                    print(f"✗ No se pudo acceder a: {group}")
            
            # Verificar grupo privado
            private_chat = await resolve_chat(app, private_group)
            if private_chat:
                print(f"✓ Acceso confirmado al grupo privado: {private_chat.title}")
            else:
                print(f"✗ No se pudo acceder al grupo privado: {private_group}")
                return
            
        except Exception as e:
            print("\nIniciando nueva sesión...")
            print("Por favor, confirma el inicio de sesión en tu app de Telegram.")
            print(f"Error: {e}")
            await asyncio.sleep(2)

        print("\nComenzando envío de tarjetas...")
        print("Presiona Ctrl+C para cancelar en cualquier momento...")

        # Obtener índice actual para cada grupo
        current_index = 0
        total_cards_sent = 0  # Contador para estadísticas
        
        while True:
            cards_sent_this_round = False
            cards_sent_in_round = 0  # Contador para esta ronda
            
            # Enviar una tarjeta diferente a cada grupo
            for group in group_list:
                # Buscar la siguiente tarjeta no enviada para este grupo
                card_found = False
                while current_index < len(cards):
                    card = cards[current_index]
                    current_index += 1
                    
                    # Si la tarjeta no ha sido enviada a este grupo
                    key = str(group)
                    if card not in state.get(key, []):
                        message = f"{prefix_map.get(key, '')} {card}"
                        sent_msg = await send_message_to_group(app, group, message)
                        if sent_msg:
                            last_sent_messages[key] = sent_msg.id
                        
                        # Actualizar estado
                        state[key].append(card)
                        save_state(state)
                        
                        card_found = True
                        cards_sent_this_round = True
                        cards_sent_in_round += 1
                        total_cards_sent += 1
                        break
                
                if not card_found:
                    print(f"\nNo hay más tarjetas disponibles para {group}")
            
            # Actualizar estadísticas en el servidor después de cada ronda
            if cards_sent_in_round > 0:
                try:
                    await update_usage_stats(len(group_list), cards_sent_in_round)
                except Exception as e:
                    print(f"⚠️  Error actualizando estadísticas: {e}")
            
            # Si no se enviaron tarjetas en esta ronda, terminar
            if not cards_sent_this_round:
                print("\n¡No quedan más tarjetas para enviar!")
                break
                
            # Esperar antes de la siguiente ronda
            print(f"\nEsperando 62 segundos antes de la siguiente ronda...")
            await asyncio.sleep(62)

        # Mantener el script ejecutándose por un tiempo adicional para recibir respuestas
        print("\nEsperando respuestas finales de los bots...")
        await asyncio.sleep(30)  # Esperar 30 segundos más para recibir respuestas
        
        # Actualización final de estadísticas
        if total_cards_sent > 0:
            print(f"\n📊 RESUMEN FINAL:")
            print(f"   💳 Total de tarjetas enviadas: {total_cards_sent}")
            print(f"   📱 Grupos utilizados: {len(group_list)}")
            try:
                await update_usage_stats(len(group_list), 0)  # Actualización final sin tarjetas adicionales
                print(f"   ✅ Estadísticas actualizadas en el servidor")
            except Exception as e:
                print(f"   ⚠️  Error en actualización final: {e}")

    except KeyboardInterrupt:
        print("\n\nEnvío cancelado por el usuario.")
    except Exception as e:
        import traceback
        print(f"\nError: {e}")
        traceback.print_exc()
    finally:
        await app.stop()
        cleanup_state()
        input("\nPresiona Enter para volver al menú...")

async def main():
    """Función principal del programa"""
    # Verificar si es la primera vez
    if check_initial_setup():
        await initial_setup()
    
    # Mostrar menú principal
    await show_main_menu()

if __name__ == "__main__":
    asyncio.run(main())
