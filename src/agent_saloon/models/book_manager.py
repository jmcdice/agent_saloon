# src/models/book_manager.py

import os
import re

class BookManager:
    def __init__(self, base_path="books"):
        self.base_path = base_path
        self._ensure_base_path()

    def _ensure_base_path(self):
        try:
            os.makedirs(self.base_path, exist_ok=True)
        except OSError as e:
            print(f"Error creating base directory {self.base_path}: {e}")
            raise

    def sanitize_title(self, title):
        """Sanitize the book title to create a valid directory name."""
        sanitized = re.sub(r'[^\w\s-]', '', title).strip().lower()
        sanitized = re.sub(r'[\s_-]+', '_', sanitized)
        return sanitized

    def create_book_directory(self, title):
        """Create a directory for the book."""
        sanitized_title = self.sanitize_title(title)
        book_path = os.path.join(self.base_path, sanitized_title)
        try:
            os.makedirs(book_path, exist_ok=True)
        except OSError as e:
            print(f"Error creating book directory {book_path}: {e}")
            raise
        return book_path

    def write_content(self, book_title, filename, content, subdir=None):
        """Write content to a file within the book's directory.
    
        Args:
            book_title (str): The title of the book.
            filename (str): The filename to write to.
            content (str): The content to write.
            subdir (str, optional): A subdirectory within the book's directory.
        """
        book_path = self.create_book_directory(book_title)
        if subdir:
            dir_path = os.path.join(book_path, subdir)
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, filename)
        else:
            file_path = os.path.join(book_path, filename)
        try:
            # Remove Consensus markers from content
            lines = content.splitlines()
            processed_lines = [line for line in lines if not line.strip().startswith("Consensus:")]
            content = '\n'.join(processed_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Written to {file_path}")
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")
            raise
    
    def read_file(self, book_title, filename, subdir=None):
        """Read content from a file within the book's directory.

        Args:
            book_title (str): The title of the book.
            filename (str): The filename to read from.
            subdir (str, optional): A subdirectory within the book's directory.

        Returns:
            str: The content of the file.
        """
        book_path = self.create_book_directory(book_title)
        if subdir:
            file_path = os.path.join(book_path, subdir, filename)
        else:
            file_path = os.path.join(book_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Read from {file_path}")
            return content
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            raise

    def write_section(self, book_title, chapter_number, section_number, content):
        """Write a section to the appropriate file.

        Args:
            book_title (str): The title of the book.
            chapter_number (str): The chapter number (e.g., '1').
            section_number (str): The section number (e.g., '1.1').
            content (str): The content of the section.
        """
        if section_number:
            filename = f"chapter_{chapter_number}_section_{section_number.replace('.', '_')}.md"
        else:
            filename = f"chapter_{chapter_number}.md"
        subdir = "sections"
        self.write_content(book_title, filename, content, subdir=subdir)

    def write_chapter(self, book_title, chapter_number, content):
        """Write a chapter to the appropriate file.

        Args:
            book_title (str): The title of the book.
            chapter_number (str): The chapter number (e.g., '1').
            content (str): The content of the chapter.
        """
        filename = f"chapter_{chapter_number}.md"
        subdir = "chapters"
        self.write_content(book_title, filename, content, subdir=subdir)

