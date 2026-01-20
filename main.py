from ui import iniciar_app
import traceback

if __name__ == "__main__":
    try:
        iniciar_app()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        input("Presiona Enter para cerrar...")
