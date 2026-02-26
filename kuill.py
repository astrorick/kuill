import sys
from app.gui import KuillApp

if __name__ == "__main__":
    app = KuillApp(databasePath = sys.argv[1])
    app.run()
