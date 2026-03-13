import sys
from app.tui import KuillApp

def main():
    app = KuillApp(library_file_path = sys.argv[1])
    app.run()

if __name__ == "__main__":
    main()
