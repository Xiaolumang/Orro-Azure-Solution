import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    logging.info('This is an info message.')

if __name__ == "__main__":
    main()
