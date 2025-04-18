#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

void read_string(FILE *f, char *buf, uint8_t len) {
    fread(buf, 1, len, f);
    buf[len] = '\0';
}

void parse_symbols(FILE *f, uint16_t count) {
    for (int i = 0; i < count; ++i) {
        uint16_t offset;
        uint8_t name_len;
        char name[256];

        fread(&offset, sizeof(uint16_t), 1, f);
        fread(&name_len, sizeof(uint8_t), 1, f);
        read_string(f, name, name_len);

        printf("  Symbol: offset=0x%04X name=%s\n", offset, name);
    }
}

void parse_segment(FILE *f) {
    uint16_t unknown, symbol_count, sym_data_size, seg_number;
    uint64_t reserved;
    uint16_t unk0, unk1;
    uint8_t name_len;
    char name[256];

    fread(&unknown, sizeof(uint16_t), 1, f);
    fread(&symbol_count, sizeof(uint16_t), 1, f);
    fread(&sym_data_size, sizeof(uint16_t), 1, f);
    fread(&seg_number, sizeof(uint16_t), 1, f);
    fread(&reserved, sizeof(uint64_t), 1, f);
    fread(&unk0, sizeof(uint16_t), 1, f);
    fread(&unk1, sizeof(uint16_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, name, name_len);

    printf("Segment #%u (%s): %u symbols\n", seg_number, name, symbol_count);
    parse_symbols(f, symbol_count);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s file.sym\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("fopen");
        return 1;
    }

    uint16_t total_syms, reserved0, unknown0, const_count, first_seg_offset, seg_count, unknown1;
    uint8_t unknown2, name_len;
    char name[256];

    fread(&total_syms, sizeof(uint16_t), 1, f);
    fread(&reserved0, sizeof(uint16_t), 1, f);
    fread(&unknown0, sizeof(uint16_t), 1, f);
    fread(&const_count, sizeof(uint16_t), 1, f);
    fread(&first_seg_offset, sizeof(uint16_t), 1, f);
    fread(&seg_count, sizeof(uint16_t), 1, f);
    fread(&unknown1, sizeof(uint16_t), 1, f);
    fread(&unknown2, sizeof(uint8_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, name, name_len);

    printf("SYM Header:\n");
    printf("  Total Symbols: %u\n", total_syms);
    printf("  Const Entries: %u\n", const_count);
    printf("  Segment Count: %u\n", seg_count);
    printf("  Binary Name: %s\n\n", name);

    // Constants follow, but format unknown — skipping to segment section
    fseek(f, first_seg_offset, SEEK_SET);

    for (int i = 0; i < seg_count; ++i) {
        parse_segment(f);
    }

    fclose(f);
    return 0;
}

