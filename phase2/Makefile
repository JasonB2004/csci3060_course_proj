# Builds the Front End into ./frontend
# Usage:  make         build (only recompiles files that changed)
#         make clean   delete everything the build made

CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra
DEPFLAGS = -MMD -MP

SRC_DIR   = src
BUILD_DIR = build
TARGET    = frontend

SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(SOURCES:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)

# Link all object files into the program
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Compile one .cpp into one .o (and a .d file listing its headers)
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(DEPFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR) $(TARGET)

.PHONY: clean

# Recompile a .cpp when a header it includes changes
-include $(OBJECTS:.o=.d)