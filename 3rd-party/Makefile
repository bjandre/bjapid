BUILD=Debug
BUILD_DIR=build-$(BUILD)
INSTALL_DIR=$(BUILD_DIR)

cmocka : FORCE
	mkdir -p $(BUILD_DIR)/$@;
	cd $(BUILD_DIR)/$@; cmake -DCMAKE_INSTALL_PREFIX=.. -DCMAKE_BUILD_TYPE=$(BUILD) -DWITH_STATIC_LIB=ON ../../cmocka; make install

clean : FORCE
	-rm -rf *~

clobber : clean
	-rm -rf $(BUILD_DIR)

FORCE :
