#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include "json5.hpp"

int main() {
    std::string line;
    std::vector<std::string> lines;

    while(std::getline(std::cin, line)) {
        if (line.empty()) { 
            break;
        }
        lines.push_back(line); 
    }

    std::stringstream ss;
    for (auto it = lines.begin(); it != lines.end(); ++it) {
        ss << *it << '\n';
    }
    std::string const inputs = ss.str();

    auto obj5 = json::parse5(inputs);
    if (!obj5) {
        std::cout << "Failed to parse!" << std::endl;
        return 1;
    } 
    std::cout << "Succeeded Parsed" << std::endl;
    return 0;
    
}
