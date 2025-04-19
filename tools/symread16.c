#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static FILE *csv = NULL;

static void read_string(FILE *f, char *buf, uint8_t len) {
    fread(buf, 1, len, f);
    buf[len] = '\0';
}

static void write_csv(uint16_t segnum, const char *segname, uint16_t offset, const char *symname) {
    if (csv) {
        fprintf(csv, "%u,%s,0x%04X,%s\n", segnum, segname, offset, symname);
    }
}

static void parse_symbols(FILE *f, uint16_t count, uint16_t segnum, const char *segname) {
    for (int i = 0; i < count; ++i) {
        uint16_t offset;
        uint8_t name_len;
        char name[256];

        fread(&offset, sizeof(uint16_t), 1, f);
        fread(&name_len, sizeof(uint8_t), 1, f);
        read_string(f, name, name_len);

        printf("  Symbol: offset=0x%04X name=%s\n", offset, name);
        write_csv(segnum, segname, offset, name);
    }
}

static void parse_segment(FILE *f) {
    uint16_t unused, sym_count, sym_size, segnum;
    uint64_t reserved;
    uint16_t unk0, unk1;
    uint8_t name_len;
    char segname[256];

    fread(&unused, sizeof(uint16_t), 1, f);
    fread(&sym_count, sizeof(uint16_t), 1, f);
    fread(&sym_size, sizeof(uint16_t), 1, f);
    fread(&segnum, sizeof(uint16_t), 1, f);
    fread(&reserved, sizeof(uint64_t), 1, f);
    fread(&unk0, sizeof(uint16_t), 1, f);
    fread(&unk1, sizeof(uint16_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, segname, name_len);

    printf("Segment #%u (%s): %u symbols\n", segnum, segname, sym_count);
    parse_symbols(f, sym_count, segnum, segname);
}

int main(int argc, char **argv) {
    const char *input_path = NULL;
    char csv_path[512] = {0};

    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "-o") && i + 1 < argc) {
            snprintf(csv_path, sizeof(csv_path), "%s/symbols.csv", argv[++i]);
        } else {
            input_path = argv[i];
        }
    }

    if (!input_path) {
        fprintf(stderr, "Usage: %s [-o output_dir] file.sym\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(input_path, "rb");
    if (!f) {
        perror("fopen input");
        return 1;
    }

    if (csv_path[0]) {
        csv = fopen(csv_path, "w");
        if (!csv) {
            perror("fopen csv");
            fclose(f);
            return 1;
        }
        fprintf(csv, "SegmentNumber,SegmentName,SymbolOffset,SymbolName\n");
    }

    uint16_t total_syms, reserved0, unknown0, const_count;
    uint16_t seg_offset, seg_count, unknown1;
    uint8_t unknown2, name_len;
    char binname[256];

    fread(&total_syms, sizeof(uint16_t), 1, f);
    fread(&reserved0, sizeof(uint16_t), 1, f);
    fread(&unknown0, sizeof(uint16_t), 1, f);
    fread(&const_count, sizeof(uint16_t), 1, f);
    fread(&seg_offset, sizeof(uint16_t), 1, f);
    fread(&seg_count, sizeof(uint16_t), 1, f);
    fread(&unknown1, sizeof(uint16_t), 1, f);
    fread(&unknown2, sizeof(uint8_t), 1, f);
    fread(&name_len, sizeof(uint8_t), 1, f);
    read_string(f, binname, name_len);

    printf("Filename: %s\n", input_path);
    printf("SYM Header:\n");
    printf("  Total Symbols: %u\n", total_syms);
    printf("  Const Entries: %u\n", const_count);
    printf("  Segment Count: %u\n", seg_count);
    printf("  Binary Name: %s\n\n", binname);

    fseek(f, seg_offset, SEEK_SET);

    for (int i = 0; i < seg_count; ++i) {
        parse_segment(f);
    }

    fclose(f);
    if (csv) fclose(csv);
    return 0;
}
