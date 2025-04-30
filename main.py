#!/usr/bin/env python3
"""
Shim to launch the Agent Saloon CLI.
"""
from agent_saloon.cli import main

if __name__ == '__main__':
    main()

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

