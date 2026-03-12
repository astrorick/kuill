import sys
from app.gui import KuillApp

def main():
    app = KuillApp(libraryFilePath = sys.argv[1])
    app.run()

if __name__ == "__main__":
    main()
