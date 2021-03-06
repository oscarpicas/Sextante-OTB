# $Id$

PROJECT(OTBTesting)

# The Testing directory is setup so it can build either as part of the
# normal OTB build or as a stand-alone project.  This design is useful
# for testing the installation tree of OTB.

FILE(MAKE_DIRECTORY ${OTBTesting_BINARY_DIR}/Temporary)

IF(OTB_BINARY_DIR)
  # We are building inside the tree.
  INCLUDE(${CMAKE_CURRENT_SOURCE_DIR}/TestingHelper.cmake)
  ADD_SUBDIRECTORY(Code)
  ADD_SUBDIRECTORY(Fa)
  ADD_SUBDIRECTORY(Utilities)
  
  IF(BUILD_APPLICATIONS)
    ADD_SUBDIRECTORY(Applications)
  ENDIF(BUILD_APPLICATIONS)
  
ELSE(OTB_BINARY_DIR)
  # We are building as a stand-alone project.
  CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

  SET(OTB_TESTING_STANDALONE ON)

  SET(LIBRARY_OUTPUT_PATH ${OTBTesting_BINARY_DIR}/bin CACHE PATH "Single output directory for building all libraries.")
  SET(EXECUTABLE_OUTPUT_PATH ${OTBTesting_BINARY_DIR}/bin CACHE PATH "Single output directory for building all executables.")
  MARK_AS_ADVANCED(LIBRARY_OUTPUT_PATH EXECUTABLE_OUTPUT_PATH)
  SET(CXX_TEST_PATH ${EXECUTABLE_OUTPUT_PATH})

  # Configure Dart testing support.
  #SET(PROJECT_SOURCE_DIR "${OTBTesting_SOURCE_DIR}/..")
  INCLUDE(${CMAKE_ROOT}/Modules/Dart.cmake)
  #SET(PROJECT_SOURCE_DIR "${OTBTesting_SOURCE_DIR}")
  MARK_AS_ADVANCED(TCL_TCLSH)
  IF(BUILD_TESTING)
    ENABLE_TESTING()
  ENDIF(BUILD_TESTING)

  # Find the data directory.
  FIND_PATH(OTB_DATA_ROOT OTBData.readme ${OTBTesting_SOURCE_DIR}/Data $ENV{OTB_DATA_ROOT})
  MARK_AS_ADVANCED(OTB_DATA_ROOT)

  OPTION(OTB_DATA_USE_LARGEINPUT "Use Large inputs images test." OFF)
  MARK_AS_ADVANCED(OTB_DATA_USE_LARGEINPUT)
  IF(OTB_DATA_USE_LARGEINPUT)
    FIND_PATH(OTB_DATA_LARGEINPUT_ROOT OTBData.readme $ENV{OTB_DATA_LARGEINPUT_ROOT})
    MARK_AS_ADVANCED(OTB_DATA_LARGEINPUT_ROOT)
  ENDIF(OTB_DATA_USE_LARGEINPUT)
  
  OPTION(OTB_DATA_USE_SPOTPHRINPUT "Use PHR data provided by SPOT." OFF)
  MARK_AS_ADVANCED(OTB_DATA_USE_SPOTPHRINPUT)
  IF(OTB_DATA_USE_SPOTPHRINPUT)
    FIND_PATH(OTB_DATA_SPOTPHRINPUT_ROOT OTB_PHR_Data.readme $ENV{OTB_DATA_SPOTPHRINPUT_ROOT})
    MARK_AS_ADVANCED(OTB_DATA_SPOTPHRINPUT_ROOT)
  ENDIF(OTB_DATA_USE_SPOTPHRINPUT)

  INCLUDE(${CMAKE_CURRENT_SOURCE_DIR}/TestingHelper.cmake)

  OPTION(OTB_DATA_USE_CNESPHRINPUT "Use PHR data provided by ICC." OFF)
  MARK_AS_ADVANCED(OTB_DATA_USE_CNESPHRINPUT)
  IF(OTB_DATA_USE_CNESPHRINPUT)
    FIND_PATH(OTB_DATA_CNESPHRINPUT_ROOT OTB_PHR_Data.readme $ENV{OTB_DATA_CNESPHRINPUT_ROOT})
    MARK_AS_ADVANCED(OTB_DATA_CNESPHRINPUT_ROOT)
  ENDIF(OTB_DATA_USE_CNESPHRINPUT)

  MACRO(OTB_ADD_EXECUTABLE name sources libraries)
    ADD_EXECUTABLE(${name} ${sources})
    TARGET_LINK_LIBRARIES(${name}  ${libraries})
    IF(OTB_CPP_CHECK_SOURCE_FILE)
      FOREACH( file ${sources})
        ADD_CUSTOM_COMMAND( TARGET ${name}
          PRE_BUILD
          COMMAND ${OTB_CPP_CHECK_PROG}
          ARGS ${CMAKE_CURRENT_SOURCE_DIR}/${file}
          DEPENDS ${libraries}
          COMMENT "============== C++ checking ${file} source file...  =================="
          VERBATIM )
      ENDFOREACH(file)
    ENDIF(OTB_CPP_CHECK_SOURCE_FILE)
  ENDMACRO(OTB_ADD_EXECUTABLE)
  
  # Find OTB and load its settings.
  FIND_PACKAGE(OTB PATHS /usr/lib/otb)
  IF(OTB_FOUND)
    INCLUDE(${OTB_USE_FILE})
    ADD_SUBDIRECTORY(Code)
  ELSE(OTB_FOUND)
    MESSAGE(FATAL_ERROR "OTB not found.  Please set OTB_DIR")
  ENDIF(OTB_FOUND)
  
  CONFIGURE_FILE(../CMake/CTestCustom.cmake.in CTestCustom.cmake)

  #Prevents conflicts with visual min/max function
  IF(WIN32)
    ADD_DEFINITIONS(-DNOMINMAX)
  ENDIF(WIN32)

ENDIF(OTB_BINARY_DIR)

IF(OTB_COMPILE_WITH_FULL_WARNING)
  IF(CMAKE_COMPILER_IS_GNUCXX)
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OTB_FULL_WARNING_LIST_PARAMETERS}")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OTB_FULL_WARNING_LIST_PARAMETERS}")
  ENDIF(CMAKE_COMPILER_IS_GNUCXX)
ENDIF(OTB_COMPILE_WITH_FULL_WARNING)

