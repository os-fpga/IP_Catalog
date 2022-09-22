cmake_minimum_required(VERSION 3.15)


find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
        set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
        set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif(CCACHE_FOUND)

if (${CMAKE_VERSION} VERSION_GREATER "3.8")
    #For cmake >= 3.9 INTERPROCEDURAL_OPTIMIZATION behaviour we need to explicitly
    #set the cmake policy version number
    cmake_policy(VERSION 3.9) 

    # If we are using verison < 3.9 then setting INTERPROCEDURAL_OPTIMIZATION
    # has no effect unless an Intel compiler is used
endif()

if(NOT CMAKE_BUILD_TYPE)
    message(WARNING "Build type not set, falling back to Release mode.
        To specify build type use:
        -DCMAKE_BUILD_TYPE=<mode> where <mode> is Debug or Release.")
    set(CMAKE_BUILD_TYPE
        "Release"
        CACHE STRING "Choose the type of build, options are: Debug Release."
        FORCE)
endif(NOT CMAKE_BUILD_TYPE)


project(IP_Catalog)

message(${PROJECT_SOURCE_DIR})

message(STATUS "IP_Catalog installation started")
find_package(Python COMPONENTS Interpreter REQUIRED)
message(${CMAKE_CURRENT_BINARY_DIR})
message(STATUS "CMAKE_CURRENT_BINARY_DIR")
message(${CMAKE_INSTALL_PREFIX})
execute_process(COMMAND wget -P ${CMAKE_CURRENT_BINARY_DIR}/ip_dependencies https://raw.githubusercontent.com/bilalahmed-RS/litex/master/litex_setup.py)
execute_process(COMMAND python3 ${CMAKE_CURRENT_BINARY_DIR}/ip_dependencies/litex_setup.py --init --install --config minimal --prefix ${CMAKE_CURRENT_BINARY_DIR}/../ip_dependencies)
execute_process(COMMAND tree ${CMAKE_INSTALL_PREFIX} -L 2)
message(STATUS "IP_Catalog installation completed")
