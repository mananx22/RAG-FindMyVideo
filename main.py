__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def main():
    print("Hello from rag-findmyvideo!")


if __name__ == "__main__":
    main()
