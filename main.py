from login import mostrar_login
import traceback

if __name__ == "__main__":
    try:
        mostrar_login()
   
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        input("Presiona Enter para cerrar...")
 