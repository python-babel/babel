bin/icu4c_date_format: icu4c_date_format.cpp
	mkdir -p bin
	$(CXX) -Wall -std=c++17 -o $@ $^ $(shell pkg-config --cflags --libs icu-uc icu-i18n)
