#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <zlib.h>

#define START 22
#define END 36
#define MAX_LINE_LENGTH 128

using namespace std;

struct LineEntry
{
    string line;
    long long key;
};

bool compare(const LineEntry &a, const LineEntry &b)
{
    return a.key < b.key;
}

void preprocess(const string &filename)
{
    gzFile file = gzopen(filename.c_str(), "r");
    vector<LineEntry> lines;
    char buffer[MAX_LINE_LENGTH];

    while (gzgets(file, buffer, MAX_LINE_LENGTH))
    {
        string line(buffer);
        string key_str = line.substr(START, END - START);
        long long key = stoll(key_str);
        lines.push_back({line, key});
    }
    gzclose(file);

    sort(lines.begin(), lines.end(), compare);

    file = gzopen(filename.c_str(), "w");
    for (const auto &entry : lines)
    {
        gzputs(file, entry.line.c_str());
    }
    gzclose(file);
}

int main(int argc, char *argv[])
{
    preprocess(argv[1]);
    return EXIT_SUCCESS;
}