def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read() 
        return content
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        

def main():
    file_path = 'face_base.txt'
    content = read_file(file_path)
    if content is not None:
        print("File Content:")
        print(content)
    
main()