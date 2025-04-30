#!/usr/bin/env python3

"""
CLI entry point for Agent Saloon.
"""
import re
import os
import argparse
from agent_saloon.models import TitleGenerator, TableOfContentsGenerator
from agent_saloon.models.book_manager import BookManager
from agent_saloon.models.section_writer import SectionWriter
from agent_saloon.utils.irc_logger import irc_logger

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
            chapter_number = chapter_match.group(1)
            chapter_title = chapter_match.group(2)
            current_chapter = {'number': chapter_number, 'title': chapter_title, 'sections': []}
            chapters.append(current_chapter)
        elif section_match and current_chapter is not None:
            section_number = section_match.group(1)
            section_title = section_match.group(2)
            current_chapter['sections'].append({'number': section_number, 'title': section_title})
    return chapters

def compile_chapters(book_manager, title, chapters):
    """
    Compile all sections of each chapter into a single chapter file.
    """
    for chapter in chapters:
        num = chapter['number']
        title_text = chapter['title']
        sections = chapter['sections']
        irc_logger.system_message(f"Compiling Chapter {num}: {title_text}")
        content = f"# Chapter {num}: {title_text}\n\n"
        if not sections:
            filename = f"chapter_{num}.md"
            path = os.path.join(book_manager.create_book_directory(title), 'sections', filename)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content += f.read()
            else:
                irc_logger.error(f"Chapter file {filename} does not exist.")
        else:
            sorted_secs = sorted(sections, key=lambda s: list(map(int, s['number'].split('.'))))
            for sec in sorted_secs:
                sn = sec['number']
                st = sec['title']
                filename = f"chapter_{num}_section_{sn.replace('.', '_')}.md"
                path = os.path.join(book_manager.create_book_directory(title), 'sections', filename)
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content += f"## Section {sn}: {st}\n\n" + f.read() + "\n\n"
                else:
                    irc_logger.error(f"Section file {filename} does not exist.")
        book_manager.write_chapter(title, num, content)
    irc_logger.system_message("All chapters have been compiled.")

def compile_final_book(book_manager, title, chapters):
    """
    Compile all chapters into the final book file.
    """
    irc_logger.system_message("Compiling the final book...")
    final = f"# {title}\n\n## Table of Contents\n\n"
    final += book_manager.read_file(title, 'table_of_contents.txt') + "\n\n"
    for chap in sorted(chapters, key=lambda c: int(c['number'])):
        filename = f"chapter_{chap['number']}.md"
        path = os.path.join(book_manager.create_book_directory(title), 'chapters', filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                final += f.read() + "\n\n"
        else:
            irc_logger.error(f"Chapter file {filename} does not exist.")
    book_manager.write_content(title, 'final_book.md', final)
    irc_logger.system_message(f"Final book compiled successfully at {os.path.join(book_manager.create_book_directory(title), 'final_book.md')}")

def main():
    parser = argparse.ArgumentParser(description="Generate a book collaboratively with AI agents.")
    parser.add_argument('-c', '--chapters', type=int, default=3, help='Number of chapters to generate')
    parser.add_argument('topic', nargs='+', help='Topic for the book')
    args = parser.parse_args()
    topic = ' '.join(args.topic).strip()
    chapter_count = args.chapters

    # Title
    title = TitleGenerator(topic).generate()
    if not title:
        return
    irc_logger.system_message(f"Final Book Title: {title}")

    manager = BookManager()
    manager.create_book_directory(title)
    manager.write_content(title, 'title.txt', title)

    # ToC
    toc = TableOfContentsGenerator(title, chapter_count).generate()
    if not toc:
        return
    irc_logger.system_message("Final Table of Contents:")
    irc_logger.print_content(toc)
    manager.write_content(title, 'table_of_contents.txt', toc)

    chapters = parse_toc(toc)
    for chap in chapters:
        num = chap['number']; t = chap['title']; secs = chap['sections']
        if not secs:
            irc_logger.system_message(f"Writing Chapter {num}: {t}")
            content = SectionWriter(title, toc, num, t).write()
            if content:
                manager.write_section(title, num, None, content)
        else:
            for sec in secs:
                sn = sec['number']; st = sec['title']
                irc_logger.system_message(f"Writing Section {sn}: {st}")
                content = SectionWriter(title, toc, sn, st).write()
                if content:
                    manager.write_section(title, num, sn, content)

    irc_logger.system_message("All sections have been processed.")
    compile_chapters(manager, title, chapters)
    compile_final_book(manager, title, chapters)

if __name__ == '__main__':
    main()