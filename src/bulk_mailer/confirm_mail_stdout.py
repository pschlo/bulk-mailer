
def ask_send_confirmation(text: str, accept: str, reject: str) -> bool:
    print(text)

    while True:
        choice = input(f"\n\n{accept}[y] / {reject}[n]: ").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print('Invalid input')
