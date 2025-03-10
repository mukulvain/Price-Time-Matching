#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <zlib.h>
#include <cstdio>
#include <csignal>
#include <queue>
#include <chrono>

#define START 22
#define END 36
#define MAX_LINE_LENGTH 128
#define CHUNK_SIZE 100000000

using namespace std;

const char *inputFile = nullptr;
void signalHandler(int signum)
{
    cerr << inputFile << " was killed by signal " << signum << "\n";
    exit(signum);
}

struct LineEntry
{
    string line;
    long long key;
};

struct Compare
{
    bool operator()(const pair<LineEntry, ifstream *> &a, const pair<LineEntry, ifstream *> &b)
    {
        return a.first.key > b.first.key;
    }
};

vector<LineEntry> readChunk(gzFile file, size_t maxLines)
{
    vector<LineEntry> lines;
    char buffer[MAX_LINE_LENGTH];
    while (lines.size() < maxLines && gzgets(file, buffer, MAX_LINE_LENGTH))
    {
        string line(buffer);
        string key_str = line.substr(START, END - START);
        long long key = stoll(key_str);
        lines.push_back({line, key});
    }
    return lines;
}

vector<string> splitAndSort(const string &filename)
{
    gzFile file = gzopen(filename.c_str(), "r");
    vector<string> chunkFiles;
    int chunkIndex = 0;

    while (!gzeof(file))
    {
        vector<LineEntry> lines = readChunk(file, CHUNK_SIZE);
        if (lines.empty())
            break;

        sort(lines.begin(), lines.end(), [](const LineEntry &a, const LineEntry &b)
             { return a.key < b.key; });

        string chunkFile = "chunk_" + to_string(chunkIndex++) + ".txt";
        ofstream out(chunkFile);
        for (const auto &entry : lines)
            out << entry.line;
        out.close();

        chunkFiles.push_back(chunkFile);
    }

    gzclose(file);
    return chunkFiles;
}

void mergeChunks(const vector<string> &chunkFiles, const string &outputFile)
{
    priority_queue<pair<LineEntry, ifstream *>, vector<pair<LineEntry, ifstream *>>, Compare> minHeap;
    vector<ifstream *> fileStreams;

    for (const auto &chunkFile : chunkFiles)
    {
        ifstream *in = new ifstream(chunkFile);
        if (!in->is_open())
            continue;

        string line;
        if (getline(*in, line))
        {
            string key_str = line.substr(START, END - START);
            long long key = stoll(key_str);
            minHeap.push({{line, key}, in});
        }

        fileStreams.push_back(in);
    }

    gzFile out = gzopen(outputFile.c_str(), "w");

    while (!minHeap.empty())
    {
        auto [entry, in] = minHeap.top();
        minHeap.pop();

        gzputs(out, (entry.line + "\n").c_str());

        string line;
        if (getline(*in, line))
        {
            string key_str = line.substr(START, END - START);
            long long key = stoll(key_str);
            minHeap.push({{line, key}, in});
        }
    }

    gzclose(out);

    for (ifstream *in : fileStreams)
    {
        in->close();
        delete in;
    }

    for (const auto &chunkFile : chunkFiles)
        remove(chunkFile.c_str());
}

int main(int argc, char *argv[])
{
    signal(SIGTERM, signalHandler);
    signal(SIGSEGV, signalHandler);
    signal(SIGABRT, signalHandler);

    inputFile = argv[1];
    string outputFile = inputFile;
    auto start = chrono::high_resolution_clock::now();

    vector<string> chunkFiles = splitAndSort(inputFile);
    mergeChunks(chunkFiles, outputFile);

    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> duration = end - start;

    cout << "File sorted: " << outputFile << "\n";
    cout << "Execution time: " << duration.count() << " seconds\n";
    return EXIT_SUCCESS;
}
