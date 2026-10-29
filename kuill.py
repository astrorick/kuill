import sys
from app.tui import KuillApp

def main():
    if len(sys.argv) != 2:
        print("Usage: python kuill.py <library_file.json>", file = sys.stderr)
        sys.exit(1)

    app = KuillApp(library_file_path = sys.argv[1])
    app.run()

if __name__ == "__main__":
    main()
