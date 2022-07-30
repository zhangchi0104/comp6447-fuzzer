CXX=g++
CXX_FLAGS_I386=-m32 -std=c++17
CXX_FLAGS_X64=-std=c++17

.PHONY: all
all: meojson_x64 meojson5_x64 meojson5_i386 meojson_i386

meojson_i386: main-meojson.cpp json.hpp
	$(CXX) $(CXX_FLAGS_I386) -o ./meojson_i386 ./main-meojson.cpp

meojson5_i386: main-meojson5.cpp json5.hpp
	$(CXX) $(CXX_FLAGS_I386) -o ./meojson5_i386 ./main-meojson5.cpp

meojson_x64: main-meojson.cpp json.hpp
	$(CXX) $(CXX_FLAGS) -o ./meojson_x64 ./main-meojson.cpp

meojson5_x64: main-meojson5.cpp json5.hpp
	$(CXX) $(CXX_FLAGS) -o ./meojson5_x64 ./main-meojson5.cpp


clean:
	rm -f ./meojson_x64 ./meojson5_x64 ./meojson5_i386 ./meojson_i386
