import sys
from app.gui import KuillApp

if __name__ == "__main__":
    app = KuillApp(libraryFilePath = sys.argv[1])
    app.run()
