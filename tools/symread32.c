#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

FILE *csv = NULL;
uint16_t current_segment = 0;
uint32_t current_segment_offset = 0;
char current_segname[256] = "";

void read_string(FILE *f, char *buf, uint8_t len) {
    fread(buf, 1, len, f);
    buf[len] = '\0';
}

void parse_symbols(FILE *f, uint16_t count, int offset32) {
    for (int i = 0; i < count; ++i) {
        uint32_t offset;
        uint8_t name_len;
        char name[256];
		
        if (offset32) {
            fread(&offset, sizeof(uint32_t), 1, f);
        } else {
            uint16_t offset16;
            fread(&offset16, sizeof(uint16_t), 1, f);
            offset = offset16;
        }
		
        fread(&name_len, sizeof(uint8_t), 1, f);
        read_string(f, name, name_len);

        uint32_t absolute_addr = current_segment_offset + offset;

        printf("  Symbol: offset=%08X address=%08X name=%s\n", offset, absolute_addr, name);
        if (csv) {
            fprintf(csv, "%u,%08X,%s,%08X,%s\n",
                    current_segment,
                    current_segment_offset,
                    current_segname,
                    offset,
                    name);
        }
    }

    // ok so it seems after the symbols there's actually some
	// increasing sequence of uint16_t's . just skip it
    for (int i = 0; i < count; i++) {
        uint16_t ign;
        fread(&ign, sizeof(uint16_t), 1, f);
    }
}

void parse_segment(FILE *f) {
    uint16_t unknown, symbol_count, sym_data_size, seg_number;
    uint64_t reserved;
    uint16_t unk0, unk1, unk00, unk01, unk02, flags;
    uint8_t name_len;
    char name[256];

    //long seg_start = ftell(f);

    fread(&unknown, sizeof(uint16_t), 1, f);
    fread(&symbol_count, sizeof(uint16_t), 1, f);
    fread(&sym_data_size, sizeof(uint16_t), 1, f);
    fread(&seg_number, sizeof(uint16_t), 1, f);
    fread(&unk00, sizeof(uint16_t), 1, f);
    fread(&unk01, sizeof(uint16_t), 1, f);
    fread(&unk02, sizeof(uint16_t), 1, f);
    fread(&flags, sizeof(uint16_t), 1, f);
    fread(&unk0, sizeof(uint16_t), 1, f);
    fread(&unk1, sizeof(uint16_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, name, name_len);

    current_segment = seg_number;
    strncpy(current_segname, name, sizeof(current_segname) - 1);
    current_segname[sizeof(current_segname) - 1] = '\0';

    current_segment_offset = unknown << 4;

    printf("\nSegment #%u (%s): offset=0x%08X, %u symbols %s\n",
        seg_number,
        name,
        current_segment_offset,
        symbol_count,
        (flags & 2) ? "(sorted alphabetically)" : "");    parse_symbols(f, symbol_count, flags & 1);

    fseek(f, unknown << 4, SEEK_SET);
}

int main(int argc, char **argv) {
    const char *input_path = NULL;
    const char *csv_path = NULL;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            csv_path = argv[++i];
        } else {
            input_path = argv[i];
        }
    }

    if (!input_path) {
        fprintf(stderr, "Usage: %s [-o output.csv] file.sym\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(input_path, "rb");
    if (!f) {
        perror("fopen");
        return 1;
    }

    if (csv_path) {
        csv = fopen(csv_path, "w");
        if (!csv) {
            perror("fopen csv");
            fclose(f);
            return 1;
        }
        fprintf(csv, "SegmentNumber,SegmentOffset,SegmentName,SymbolOffset,SymbolName\n");
    }

    uint16_t total_syms, reserved0, unknown0, const_count, first_seg_offset, seg_count, seg_offs;
    uint8_t unknown2, name_len;
    char filename[256];

    fread(&total_syms, sizeof(uint16_t), 1, f);
    fread(&reserved0, sizeof(uint16_t), 1, f);
    fread(&unknown0, sizeof(uint16_t), 1, f);
    fread(&const_count, sizeof(uint16_t), 1, f);
    fread(&first_seg_offset, sizeof(uint16_t), 1, f);
    fread(&seg_count, sizeof(uint16_t), 1, f);
    fread(&seg_offs, sizeof(uint16_t), 1, f);
    fread(&unknown2, sizeof(uint8_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, filename, name_len);

    printf("Filename: %s\n", input_path);
    printf("SYM Header:\n");
    printf("  Total Symbols: %u\n", total_syms);
    printf("  Const Entries: %u\n", const_count);
    printf("  Segment Count: %u\n", seg_count);
    printf("  Binary Name: %s\n", filename);

    fseek(f, seg_offs << 4, SEEK_SET);

    for (int i = 0; i < seg_count; ++i) {
        parse_segment(f);
    }

    fclose(f);
    if (csv) fclose(csv);
    return 0;
}
