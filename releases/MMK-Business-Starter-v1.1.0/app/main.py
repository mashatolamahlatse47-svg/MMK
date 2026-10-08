def show_menu():
    print()
    print("=" * 40)
    print("       MMK BUSINESS STARTER")
    print("=" * 40)
    print("1. Business Information")
    print("2. Products")
    print("3. Customers")
    print("4. Sales")
    print("5. Reports")
    print("0. Exit")
    print("=" * 40)


def main():
    while True:
        show_menu()

        choice = input("Select an option: ")

        if choice == "1":
            print("Business Information selected.")

        elif choice == "2":
            print("Products selected.")

        elif choice == "3":
            print("Customers selected.")

        elif choice == "4":
            print("Sales selected.")

        elif choice == "5":
            print("Reports selected.")

        elif choice == "0":
            print("MMK Business Starter closed.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
