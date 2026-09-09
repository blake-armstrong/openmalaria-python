list (REMOVE_ITEM CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

find_package (Python 3.9 COMPONENTS Interpreter Development.Module REQUIRED)

execute_process (
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE NB_DIR
)
list (APPEND CMAKE_PREFIX_PATH "${NB_DIR}")
find_package (nanobind CONFIG REQUIRED)

set_target_properties (model schema contrib PROPERTIES POSITION_INDEPENDENT_CODE ON)

nanobind_add_module (_openmalaria src/bindings.cpp)

target_include_directories (_openmalaria PRIVATE
  ${CMAKE_SOURCE_DIR}/model
  ${CMAKE_BINARY_DIR}
  ${CMAKE_BINARY_DIR}/model
)

target_link_libraries (_openmalaria PRIVATE
  model
  schema
  contrib
  ${GSL_LIBRARIES}
  ${XERCESC_LIBRARIES}
  ${Z_LIBRARIES}
  ${PTHREAD_LIBRARIES}
)

install (TARGETS _openmalaria LIBRARY DESTINATION openmalaria)
