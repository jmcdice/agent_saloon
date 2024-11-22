#!/usr/bin/env python3

import re
import os
from src.models import TitleGenerator, TableOfContentsGenerator
from src.models.book_manager import BookManager
from src.models.section_writer import SectionWriter
from src.utils.irc_logger import irc_logger  # Adjust the import path accordingly

def parse_toc(toc):
    """
    Parse the Table of Contents into a structured list.

    Args:
        toc (str): The Table of Contents as a string.

    Returns:
        list: A list of dictionaries representing chapters and their sections.
    """
    chapters = []
    current_chapter = None

    for line in toc.split('\n'):
        line = line.strip()
        if not line:
            continue
        chapter_match = re.match(r'^(\d+)\.\s+(.*)', line)
        section_match = re.match(r'^(\d+\.\d+)\.\s+(.*)', line)
        
        if chapter_match and not section_match:
            # Chapter line
            chapter_number = chapter_match.group(1)
            chapter_title = chapter_match.group(2)
            current_chapter = {
                'number': chapter_number,
                'title': chapter_title,
                'sections': []
            }
            chapters.append(current_chapter)
        elif section_match:
            # Section line
            section_number = section_match.group(1)
            section_title = section_match.group(2)
            if current_chapter is not None:
                current_chapter['sections'].append({
                    'number': section_number,
                    'title': section_title
                })
    return chapters

def compile_chapters(book_manager, title, chapters):
    """
    Compile all sections of each chapter into a single chapter file.

    Args:
        book_manager (BookManager): Instance of BookManager.
        title (str): Title of the book.
        chapters (list): List of chapter dictionaries.
    """
    for chapter in chapters:
        chapter_number = chapter['number']
        chapter_title = chapter['title']
        sections = chapter['sections']

        irc_logger.system_message(f"Compiling Chapter {chapter_number}: {chapter_title}")

        # Initialize content with chapter title
        chapter_content = f"# Chapter {chapter_number}: {chapter_title}\n\n"

        if not sections:
            # No sub-sections; use the chapter content itself
            section_filename = f"chapter_{chapter_number}.md"
            section_path = os.path.join(book_manager.create_book_directory(title), "sections", section_filename)
            if os.path.exists(section_path):
                with open(section_path, 'r', encoding='utf-8') as f:
                    chapter_content += f.read()
            else:
                irc_logger.error(f"Chapter file {section_filename} does not exist.")
        else:
            # Compile all sections
            # Sort sections by section number to maintain order
            sorted_sections = sorted(sections, key=lambda s: list(map(int, s['number'].split('.'))))
            for section in sorted_sections:
                section_number = section['number']
                section_title = section['title']
                section_filename = f"chapter_{chapter_number}_section_{section_number.replace('.', '_')}.md"
                section_path = os.path.join(book_manager.create_book_directory(title), "sections", section_filename)
                if os.path.exists(section_path):
                    with open(section_path, 'r', encoding='utf-8') as f:
                        # Optionally, include section titles
                        chapter_content += f"## Section {section_number}: {section_title}\n\n"
                        chapter_content += f.read() + "\n\n"
                else:
                    irc_logger.error(f"Section file {section_filename} does not exist.")

        # Write the compiled chapter to the 'chapters' directory
        book_manager.write_chapter(title, chapter_number, chapter_content)

    irc_logger.system_message("All chapters have been compiled.")

def compile_final_book(book_manager, title, chapters):
    """
    Compile all chapters into the final book file.

    Args:
        book_manager (BookManager): Instance of BookManager.
        title (str): Title of the book.
        chapters (list): List of chapter dictionaries.
    """
    irc_logger.system_message("Compiling the final book...")

    final_book_content = f"# {title}\n\n"
    final_book_content += "## Table of Contents\n\n"
    final_book_content += book_manager.read_file(title, "table_of_contents.txt") + "\n\n"

    # Sort chapters by chapter number to maintain order
    sorted_chapters = sorted(chapters, key=lambda c: int(c['number']))
    for chapter in sorted_chapters:
        chapter_number = chapter['number']
        chapter_title = chapter['title']
        chapter_filename = f"chapter_{chapter_number}.md"
        chapter_path = os.path.join(book_manager.create_book_directory(title), "chapters", chapter_filename)
        if os.path.exists(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8') as f:
                final_book_content += f.read() + "\n\n"
        else:
            irc_logger.error(f"Chapter file {chapter_filename} does not exist.")

    # Write the final book to the book directory
    final_book_filename = "final_book.md"
    book_manager.write_content(title, final_book_filename, final_book_content)

    irc_logger.system_message(f"Final book compiled successfully at {os.path.join(book_manager.create_book_directory(title), final_book_filename)}")

def main():
    irc_logger.system_message("Enter a book topic:")
    topic = input().strip()

    # Generate title
    title_gen = TitleGenerator(topic)
    title = title_gen.generate()

    if title:
        irc_logger.system_message(f"Final Book Title: {title}")
    else:
        irc_logger.error("Failed to generate a book title.")
        return  # Exit if title generation fails

    # Initialize BookManager
    book_manager = BookManager()

    # Create book directory
    book_path = book_manager.create_book_directory(title)
    irc_logger.system_message(f"Book directory created at: {book_path}")

    # Save the book title
    book_manager.write_content(title, "title.txt", title)

    # Generate Table of Contents
    toc_generator = TableOfContentsGenerator(title)
    toc = toc_generator.generate()

    if toc:
        irc_logger.system_message("Final Table of Contents:")
        irc_logger.print_content(toc)
        # Save the ToC
        book_manager.write_content(title, "table_of_contents.txt", toc)
    else:
        irc_logger.error("Failed to generate the table of contents.")
        return  # Exit if ToC generation fails

    # Parse the ToC
    chapters = parse_toc(toc)

    # Loop through each chapter and section
    for chapter in chapters:
        chapter_number = chapter['number']
        chapter_title = chapter['title']
        
        if not chapter['sections']:
            # No sub-sections; treat the chapter itself as a section
            irc_logger.system_message(f"Writing Chapter {chapter_number}: {chapter_title}")

            # print("\nDebug values before creating SectionWriter:")
            # print(f"title: {title}")
            # print(f"toc: {toc}")
            # print(f"chapter_number: {chapter_number}")
            # print(f"chapter_title: {chapter_title}")
            
            # Create a SectionWriter instance for the chapter
            section_writer = SectionWriter(
                book_title=title,
                full_toc=toc,
                section_number=chapter_number,
                section_title=chapter_title
            )

            # Generate the chapter content
            section_content = section_writer.write()

            if section_content:
                # Write the chapter content to the filesystem
                book_manager.write_section(title, chapter_number, None, section_content)
            else:
                irc_logger.error(f"Failed to write Chapter {chapter_number}.")
        else:
            # Process each sub-section
            for section in chapter['sections']:
                section_number = section['number']
                section_title = section['title']

                irc_logger.system_message(f"Writing Section {section_number}: {section_title}")

                # Create a SectionWriter instance
                section_writer = SectionWriter(
                    book_title=title,
                    full_toc=toc,
                    section_number=section_number,
                    section_title=section_title
                )

                # Generate the section content
                section_content = section_writer.write()

                if section_content:
                    # Write the section content to the filesystem
                    book_manager.write_section(title, chapter_number, section_number, section_content)
                else:
                    irc_logger.error(f"Failed to write Section {section_number}.")

    irc_logger.system_message("All sections have been processed.")

    # Compile sections into chapters
    compile_chapters(book_manager, title, chapters)

    # Compile chapters into the final book
    compile_final_book(book_manager, title, chapters)

if __name__ == "__main__":
    main()

