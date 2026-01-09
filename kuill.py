from gui import KuillApp

def main() -> None:
    app = KuillApp(databasePath = "kuill.json")
    app.run()

if __name__ == "__main__":
    main()
