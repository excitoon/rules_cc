import unittest
from google.protobuf import text_format
from third_party.com.github.bazelbuild.bazel.src.main.protobuf import crosstool_config_pb2
from tools.migration.legacy_fields_migration_lib import ALL_COMPILE_ACTIONS
from tools.migration.legacy_fields_migration_lib import ALL_CXX_COMPILE_ACTIONS
from tools.migration.legacy_fields_migration_lib import ALL_LINK_ACTIONS
from tools.migration.legacy_fields_migration_lib import DYNAMIC_LIBRARY_LINK_ACTIONS
from tools.migration.legacy_fields_migration_lib import migrate_legacy_fields


def assert_has_feature(self, toolchain, name):
  self.assertTrue(any(feature.name == name for feature in toolchain.feature))


def make_crosstool(string):
  crosstool = crosstool_config_pb2.CrosstoolRelease()
  text_format.Merge("major_version: '123' minor_version: '456'", crosstool)
  toolchain = crosstool.toolchain.add()
  text_format.Merge(string, toolchain)
  return crosstool


def migrate_to_string(crosstool):
  migrate_legacy_fields(crosstool)
  return to_string(crosstool)


def to_string(crosstool):
  return text_format.MessageToString(crosstool)


class LegacyFieldsMigrationLibTest(unittest.TestCase):

  def test_deletes_fields(self):
    crosstool = make_crosstool("""
          debian_extra_requires: 'debian-1'
          gcc_plugin_compiler_flag: 'gcc_plugin_compiler_flag-1'
          ar_flag: 'ar_flag-1'
          ar_thin_archives_flag: 'ar_thin_archives_flag-1'
          gcc_plugin_header_directory: 'gcc_plugin_header_directory-1'
          mao_plugin_header_directory: 'mao_plugin_header_directory-1'
          default_python_top: 'default_python_top-1'
          default_python_version: 'default_python_version-1'
          python_preload_swigdeps: false
          supports_normalizing_ar: false
          supports_thin_archives: false
          supports_incremental_linker: false
          supports_dsym: false
          supports_gold_linker: false
          needsPic: false
          supports_start_end_lib: false
          supports_interface_shared_objects: false
          supports_fission: false
          static_runtimes_filegroup: 'yolo'
          dynamic_runtimes_filegroup: 'yolo'
      """)
    output = migrate_to_string(crosstool)
    self.assertNotIn("debian_extra_requires", output)
    self.assertNotIn("gcc_plugin_compiler_flag", output)
    self.assertNotIn("ar_flag", output)
    self.assertNotIn("ar_thin_archives_flag", output)
    self.assertNotIn("gcc_plugin_header_directory", output)
    self.assertNotIn("mao_plugin_header_directory", output)
    self.assertNotIn("supports_normalizing_ar", output)
    self.assertNotIn("supports_thin_archives", output)
    self.assertNotIn("supports_incremental_linker", output)
    self.assertNotIn("supports_dsym", output)
    self.assertNotIn("default_python_top", output)
    self.assertNotIn("default_python_version", output)
    self.assertNotIn("python_preload_swigdeps", output)
    self.assertNotIn("supports_gold_linker", output)
    self.assertNotIn("needsPic", output)
    self.assertNotIn("supports_start_end_lib", output)
    self.assertNotIn("supports_interface_shared_objects", output)
    self.assertNotIn("supports_fission", output)
    self.assertNotIn("static_runtimes_filegroup", output)
    self.assertNotIn("dynamic_runtimes_filegroup", output)

  def test_deletes_default_toolchains(self):
    crosstool = make_crosstool("")
    crosstool.default_toolchain.add()
    self.assertEqual(len(crosstool.default_toolchain), 1)
    migrate_legacy_fields(crosstool)
    self.assertEqual(len(crosstool.default_toolchain), 0)

  def test_migrate_compiler_flags(self):
    crosstool = make_crosstool("""
        compiler_flag: 'clang-flag-1'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.compiler_flag), 0)
    self.assertEqual(output.feature[0].name, "default_compile_flags")
    self.assertEqual(output.feature[0].flag_set[0].action, ALL_COMPILE_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["clang-flag-1"])

  def test_migrate_cxx_flags(self):
    crosstool = make_crosstool("""
        cxx_flag: 'clang-flag-1'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.cxx_flag), 0)
    self.assertEqual(output.feature[0].name, "default_compile_flags")
    self.assertEqual(output.feature[0].flag_set[0].action,
                     ALL_CXX_COMPILE_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["clang-flag-1"])

  def test_compiler_flag_come_before_cxx_flags(self):
    crosstool = make_crosstool("""
        compiler_flag: 'clang-flag-1'
        cxx_flag: 'clang-flag-2'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "default_compile_flags")
    self.assertEqual(output.feature[0].flag_set[0].action, ALL_COMPILE_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[1].action,
                     ALL_CXX_COMPILE_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["clang-flag-1"])
    self.assertEqual(output.feature[0].flag_set[1].flag_group[0].flag,
                     ["clang-flag-2"])

  def test_migrate_linker_flags(self):
    crosstool = make_crosstool("""
        linker_flag: 'linker-flag-1'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.linker_flag), 0)
    self.assertEqual(output.feature[0].name, "default_link_flags")
    self.assertEqual(output.feature[0].flag_set[0].action, ALL_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["linker-flag-1"])

  def test_migrate_dynamic_library_linker_flags(self):
    crosstool = make_crosstool("""
        dynamic_library_linker_flag: 'linker-flag-1'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.linker_flag), 0)
    self.assertEqual(output.feature[0].name, "default_link_flags")
    self.assertEqual(output.feature[0].flag_set[0].action,
                     DYNAMIC_LIBRARY_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["linker-flag-1"])

  def test_compilation_mode_flags(self):
    crosstool = make_crosstool("""
        compiler_flag: "compile-flag-1"
        cxx_flag: "cxx-flag-1"
        linker_flag: "linker-flag-1"
        compilation_mode_flags {
          mode: OPT
          compiler_flag: "opt-flag-1"
          cxx_flag: "opt-flag-2"
          linker_flag: "opt-flag-3"
        }
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.compilation_mode_flags), 0)
    assert_has_feature(self, output, "opt")

    self.assertEqual(output.feature[0].name, "default_compile_flags")
    self.assertEqual(output.feature[1].name, "default_link_flags")

    # flag set for compiler_flag fields
    self.assertEqual(len(output.feature[0].flag_set[0].with_feature), 0)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["compile-flag-1"])

    # flag set for cxx_flag fields
    self.assertEqual(len(output.feature[0].flag_set[1].with_feature), 0)
    self.assertEqual(output.feature[0].flag_set[1].flag_group[0].flag,
                     ["cxx-flag-1"])

    # flag set for compiler_flag from compilation_mode_flags
    self.assertEqual(len(output.feature[0].flag_set[2].with_feature), 1)
    self.assertEqual(output.feature[0].flag_set[2].with_feature[0].feature[0],
                     "opt")
    self.assertEqual(output.feature[0].flag_set[2].flag_group[0].flag,
                     ["opt-flag-1"])

    # flag set for cxx_flag from compilation_mode_flags
    self.assertEqual(len(output.feature[0].flag_set[3].with_feature), 1)
    self.assertEqual(output.feature[0].flag_set[3].with_feature[0].feature[0],
                     "opt")
    self.assertEqual(output.feature[0].flag_set[3].flag_group[0].flag,
                     ["opt-flag-2"])

    # default_link_flags, flag set for linker_flag
    self.assertEqual(len(output.feature[1].flag_set[0].with_feature), 0)
    self.assertEqual(output.feature[1].flag_set[0].flag_group[0].flag,
                     ["linker-flag-1"])

    # default_link_flags, flag set for linker_flag from
    # compilation_mode_flags
    self.assertEqual(len(output.feature[1].flag_set[1].with_feature), 1)
    self.assertEqual(output.feature[1].flag_set[1].with_feature[0].feature[0],
                     "opt")
    self.assertEqual(output.feature[1].flag_set[1].flag_group[0].flag,
                     ["opt-flag-3"])

  def test_linking_mode_flags(self):
    crosstool = make_crosstool("""
        linker_flag: "linker-flag-1"
        compilation_mode_flags {
          mode: DBG
          linker_flag: "dbg-flag-1"
        }
        linking_mode_flags {
          mode: MOSTLY_STATIC
          linker_flag: "mostly-static-flag-1"
        }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.compilation_mode_flags), 0)
    self.assertEqual(len(output.linking_mode_flags), 0)

    # flag set for linker_flag
    self.assertEqual(len(output.feature[0].flag_set[0].with_feature), 0)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["linker-flag-1"])

    # flag set for compilation_mode_flags
    self.assertEqual(len(output.feature[0].flag_set[1].with_feature), 1)
    self.assertEqual(output.feature[0].flag_set[1].with_feature[0].feature[0],
                     "dbg")
    self.assertEqual(output.feature[0].flag_set[1].flag_group[0].flag,
                     ["dbg-flag-1"])

    # flag set for linking_mode_flags
    self.assertEqual(len(output.feature[0].flag_set[2].with_feature), 1)
    self.assertEqual(output.feature[0].flag_set[2].with_feature[0].feature[0],
                     "static_linking_mode")
    self.assertEqual(output.feature[0].flag_set[2].flag_group[0].flag,
                     ["mostly-static-flag-1"])

  def test_coverage_compilation_mode_ignored(self):
    crosstool = make_crosstool("""
    compilation_mode_flags {
      mode: COVERAGE
      compiler_flag: "coverage-flag-1"
      cxx_flag: "coverage-flag-2"
      linker_flag: "coverage-flag-3"
    }
    """)
    output = migrate_to_string(crosstool)
    self.assertNotIn("compilation_mode_flags", output)
    self.assertNotIn("coverage-flag-1", output)
    self.assertNotIn("coverage-flag-2", output)
    self.assertNotIn("coverage-flag-3", output)
    self.assertNotIn("COVERAGE", output)

  def test_supports_dynamic_linker_when_dynamic_library_linker_flag_is_used(
      self):
    crosstool = make_crosstool("""
        dynamic_library_linker_flag: "foo"
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "default_link_flags")
    self.assertEqual(output.feature[1].name, "supports_dynamic_linker")
    self.assertEqual(output.feature[1].enabled, True)

  def test_supports_dynamic_linker_is_added_when_DYNAMIC_present(self):
    crosstool = make_crosstool("""
    linking_mode_flags {
      mode: DYNAMIC
    }
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_dynamic_linker")
    self.assertEqual(output.feature[0].enabled, True)

  def test_supports_dynamic_linker_is_not_added_when_present(self):
    crosstool = make_crosstool("""
    feature { name: "supports_dynamic_linker" enabled: false }
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_dynamic_linker")
    self.assertEqual(output.feature[0].enabled, False)

  def test_all_linker_flag_ordering(self):
    crosstool = make_crosstool("""
    linker_flag: 'linker-flag-1'
    compilation_mode_flags {
        mode: OPT
        linker_flag: 'cmf-flag-2'
    }
    linking_mode_flags {
      mode: MOSTLY_STATIC
      linker_flag: 'lmf-flag-3'
    }
    dynamic_library_linker_flag: 'dl-flag-4'
    test_only_linker_flag: 'to-flag-5'
    """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "default_link_flags")
    self.assertEqual(output.feature[0].enabled, True)
    self.assertEqual(output.feature[0].flag_set[0].action[:], ALL_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag[:],
                     ["linker-flag-1"])
    self.assertEqual(output.feature[0].flag_set[1].action[:], ALL_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[1].with_feature[0].feature[0],
                     "opt")
    self.assertEqual(output.feature[0].flag_set[1].flag_group[0].flag[:],
                     ["cmf-flag-2"])
    self.assertEqual(output.feature[0].flag_set[2].action[:], ALL_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[2].with_feature[0].feature[0],
                     "static_linking_mode")
    self.assertEqual(output.feature[0].flag_set[2].flag_group[0].flag[:],
                     ["lmf-flag-3"])
    self.assertEqual(output.feature[0].flag_set[3].action[:],
                     DYNAMIC_LIBRARY_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[3].flag_group[0].flag[:],
                     ["dl-flag-4"])
    self.assertEqual(output.feature[0].flag_set[4].action[:], ALL_LINK_ACTIONS)
    self.assertEqual(output.feature[0].flag_set[4].flag_group[0].flag[:],
                     ["to-flag-5"])
    self.assertEqual(
        output.feature[0].flag_set[4].flag_group[0].expand_if_all_available[:],
        ["is_cc_test"])

  def test_linking_mode_features_are_not_added_when_present(self):
    crosstool = make_crosstool("""
    linking_mode_flags {
      mode: DYNAMIC
      linker_flag: 'dynamic-flag'
    }
    linking_mode_flags {
      mode: FULLY_STATIC
      linker_flag: 'fully-static-flag'
    }
    linking_mode_flags {
      mode: MOSTLY_STATIC
      linker_flag: 'mostly-static-flag'
    }
    linking_mode_flags {
      mode: MOSTLY_STATIC_LIBRARIES
      linker_flag: 'mostly-static-libraries-flag'
    }
    feature { name: "static_linking_mode" }
    feature { name: "dynamic_linking_mode" }
    feature { name: "static_linking_mode_nodeps_library" }
    feature { name: "fully_static_link" }
    """)
    output = migrate_to_string(crosstool)
    self.assertNotIn("linking_mode_flags", output)
    self.assertNotIn("DYNAMIC", output)
    self.assertNotIn("MOSTLY_STATIC", output)
    self.assertNotIn("MOSTLY_STATIC_LIBRARIES", output)
    self.assertNotIn("MOSTLY_STATIC_LIBRARIES", output)
    self.assertNotIn("dynamic-flag", output)
    self.assertNotIn("fully-static-flag", output)
    self.assertNotIn("mostly-static-flag", output)
    self.assertNotIn("mostly-static-libraries-flag", output)

  def test_unfiltered_compile_flags_is_not_added_when_already_present(self):
    crosstool = make_crosstool("""
            unfiltered_cxx_flag: 'unfiltered-flag-1'
            feature { name: 'something_else' }
            feature { name: 'unfiltered_compile_flags' }
            feature { name: 'something_else_2' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(output.feature[1].name, "unfiltered_compile_flags")
    self.assertEqual(output.feature[1].flag_set[0].action, ALL_COMPILE_ACTIONS)
    self.assertEqual(output.feature[1].flag_set[0].flag_group[0].flag,
                     ["unfiltered-flag-1"])
    self.assertEqual(output.feature[2].name, "something_else_2")

  def test_unfiltered_compile_flags_is_added_at_the_end(self):
    crosstool = make_crosstool("""
            feature { name: 'something_else' }
            unfiltered_cxx_flag: 'unfiltered-flag-1'
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(output.feature[1].name, "unfiltered_compile_flags")
    self.assertEqual(output.feature[1].flag_set[0].action, ALL_COMPILE_ACTIONS)
    self.assertEqual(output.feature[1].flag_set[0].flag_group[0].flag,
                     ["unfiltered-flag-1"])

  def test_default_link_flags_is_added_first(self):
    crosstool = make_crosstool("""
          linker_flag: 'linker-flag-1'
          feature { name: 'something_else' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "default_link_flags")
    self.assertEqual(output.feature[0].enabled, True)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["linker-flag-1"])

  def test_default_link_flags_is_not_added_when_already_present(self):
    crosstool = make_crosstool("""
            linker_flag: 'linker-flag-1'
            feature { name: 'something_else' }
            feature { name: 'default_link_flags' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(output.feature[1].name, "default_link_flags")

  def test_default_compile_flags_is_not_added_when_no_reason_to(self):
    crosstool = make_crosstool("""
          feature { name: 'something_else' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(len(output.feature), 1)

  def test_default_compile_flags_is_first(self):
    crosstool = make_crosstool("""
          compiler_flag: 'compiler-flag-1'
          feature { name: 'something_else' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "default_compile_flags")
    self.assertEqual(output.feature[0].enabled, True)
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag,
                     ["compiler-flag-1"])

  def test_default_compile_flags_not_added_when_present(self):
    crosstool = make_crosstool("""
          compiler_flag: 'compiler-flag-1'
          feature { name: 'something_else' }
          feature { name: 'default_compile_flags' }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(output.feature[1].name, "default_compile_flags")
    self.assertEqual(len(output.feature[1].flag_set), 0)

  def test_supports_start_end_lib_migrated(self):
    crosstool = make_crosstool("supports_start_end_lib: true")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_start_end_lib")
    self.assertEqual(output.feature[0].enabled, True)

  def test_supports_start_end_lib_not_migrated_on_false(self):
    crosstool = make_crosstool("supports_start_end_lib: false")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.feature), 0)

  def test_supports_start_end_lib_not_migrated_when_already_present(self):
    crosstool = make_crosstool("""
            supports_start_end_lib: true
            feature { name: "supports_start_end_lib" enabled: false }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_start_end_lib")
    self.assertEqual(output.feature[0].enabled, False)

  def test_supports_interface_shared_libraries_migrated(self):
    crosstool = make_crosstool("supports_interface_shared_objects: true")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name,
                     "supports_interface_shared_libraries")
    self.assertEqual(output.feature[0].enabled, True)

  def test_supports_interface_shared_libraries_not_migrated_on_false(self):
    crosstool = make_crosstool("supports_interface_shared_objects: false")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.feature), 0)

  def test_supports_interface_shared_libraries_not_migrated_when_present(self):
    crosstool = make_crosstool("""
            supports_interface_shared_objects: true
            feature {
              name: "supports_interface_shared_libraries"
              enabled: false }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name,
                     "supports_interface_shared_libraries")
    self.assertEqual(output.feature[0].enabled, False)

  def test_supports_embedded_runtimes_migrated(self):
    crosstool = make_crosstool("supports_embedded_runtimes: true")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "static_link_cpp_runtimes")
    self.assertEqual(output.feature[0].enabled, True)

  def test_supports_embedded_runtimes_not_migrated_on_false(self):
    crosstool = make_crosstool("supports_embedded_runtimes: false")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.feature), 0)

  def test_supports_embedded_runtimes_not_migrated_when_already_present(self):
    crosstool = make_crosstool("""
            supports_embedded_runtimes: true
            feature { name: "static_link_cpp_runtimes" enabled: false }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "static_link_cpp_runtimes")
    self.assertEqual(output.feature[0].enabled, False)

  def test_needs_pic_migrated(self):
    crosstool = make_crosstool("needsPic: true")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_pic")
    self.assertEqual(output.feature[0].enabled, True)

  def test_needs_pic_not_migrated_on_false(self):
    crosstool = make_crosstool("needsPic: false")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.feature), 0)

  def test_needs_pic_not_migrated_when_already_present(self):
    crosstool = make_crosstool("""
            needsPic: true
            feature { name: "supports_pic" enabled: false }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "supports_pic")
    self.assertEqual(output.feature[0].enabled, False)

  def test_supports_fission_migrated(self):
    crosstool = make_crosstool("supports_fission: true")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "per_object_debug_info")
    self.assertEqual(output.feature[0].enabled, False)

  def test_supports_fission_not_migrated_on_false(self):
    crosstool = make_crosstool("supports_fission: false")
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(len(output.feature), 0)

  def test_supports_fission_not_migrated_when_already_present(self):
    crosstool = make_crosstool("""
            supports_fission: true
            feature { name: "per_object_debug_info" enabled: false }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "per_object_debug_info")
    self.assertEqual(output.feature[0].enabled, False)

  def test_migrating_objcopy_embed_flag(self):
    crosstool = make_crosstool("""
            objcopy_embed_flag: "a"
            objcopy_embed_flag: "b"
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "objcopy_embed_flags")
    self.assertEqual(output.feature[0].enabled, True)
    self.assertEqual(output.feature[0].flag_set[0].action[:],
                     ["objcopy_embed_data"])
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag[:],
                     ["a", "b"])
    self.assertEqual(len(output.objcopy_embed_flag), 0)

  def test_not_migrating_objcopy_embed_flag_when_feature_present(self):
    crosstool = make_crosstool("""
            objcopy_embed_flag: "a"
            objcopy_embed_flag: "b"
            feature { name: "objcopy_embed_flags" }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "objcopy_embed_flags")
    self.assertEqual(output.feature[0].enabled, False)

  def test_migrating_ld_embed_flag(self):
    crosstool = make_crosstool("""
            ld_embed_flag: "a"
            ld_embed_flag: "b"
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "ld_embed_flags")
    self.assertEqual(output.feature[0].enabled, True)
    self.assertEqual(output.feature[0].flag_set[0].action[:], ["ld_embed_data"])
    self.assertEqual(output.feature[0].flag_set[0].flag_group[0].flag[:],
                     ["a", "b"])
    self.assertEqual(len(output.ld_embed_flag), 0)

  def test_not_migrating_objcopy_embed_flag_when_feature_present(self):
    crosstool = make_crosstool("""
            objcopy_embed_flag: "a"
            objcopy_embed_flag: "b"
            feature { name: "objcopy_embed_flags" }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.feature[0].name, "objcopy_embed_flags")
    self.assertEqual(output.feature[0].enabled, False)

  def test_migrate_expand_if_all_available_from_flag_sets(self):
    crosstool = make_crosstool("""
        action_config {
          action_name: 'something'
          config_name: 'something'
          flag_set {
            expand_if_all_available: 'foo'
            flag_group {
              flag: '%{foo}'
            }
            flag_group {
              expand_if_all_available: 'bar'
              flag: 'bar'
            }
          }
        }
        feature {
          name: 'something_else'
          flag_set {
            action: 'c-compile'
            expand_if_all_available: 'foo'
            flag_group {
              flag: '%{foo}'
            }
            flag_group {
              expand_if_all_available: 'bar'
              flag: 'bar'
            }
          }
        }
        """)
    migrate_legacy_fields(crosstool)
    output = crosstool.toolchain[0]
    self.assertEqual(output.action_config[0].action_name, "something")
    self.assertEqual(len(output.action_config[0].flag_set), 1)
    self.assertEqual(
        len(output.action_config[0].flag_set[0].expand_if_all_available), 0)
    self.assertEqual(len(output.action_config[0].flag_set[0].flag_group), 2)
    self.assertEqual(
        output.action_config[0].flag_set[0].flag_group[0]
        .expand_if_all_available, ["foo"])
    self.assertEqual(
        output.action_config[0].flag_set[0].flag_group[1]
        .expand_if_all_available, ["bar", "foo"])

    self.assertEqual(output.feature[0].name, "something_else")
    self.assertEqual(len(output.feature[0].flag_set), 1)
    self.assertEqual(
        len(output.feature[0].flag_set[0].expand_if_all_available), 0)
    self.assertEqual(len(output.feature[0].flag_set[0].flag_group), 2)
    self.assertEqual(
        output.feature[0].flag_set[0].flag_group[0].expand_if_all_available,
        ["foo"])
    self.assertEqual(
        output.feature[0].flag_set[0].flag_group[1].expand_if_all_available,
        ["bar", "foo"])


if __name__ == "__main__":
  unittest.main()