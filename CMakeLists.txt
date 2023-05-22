cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(To4D)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/To4D")
set(EXTENSION_CATEGORY "Sequences")
set(EXTENSION_CONTRIBUTORS "Lucius (BNUAI)")
set(EXTENSION_DESCRIPTION "An extension which bundles 3D volumes into a 4D Sequence.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/To4D.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/To4D/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Bundler)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
