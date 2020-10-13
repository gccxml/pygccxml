# Copyright 2014-2020 Insight Software Consortium.
# Copyright 2004-2009 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

import re
import subprocess
import unittest

from . import parser_test_case

from pygccxml import parser
from pygccxml import declarations


class Test(parser_test_case.parser_test_case_t):
    global_ns = None

    def __init__(self, *args):
        parser_test_case.parser_test_case_t.__init__(self, *args)
        self.header = "test_comments.hpp"
        self.global_ns = None
        self.config.castxml_epic_version = 1

    def setUp(self):

        if not self.global_ns:
            decls = parser.parse([self.header], self.config)
            Test.global_ns = declarations.get_global_namespace(decls)
            Test.xml_generator_from_xml_file = \
                self.config.xml_generator_from_xml_file
        self.xml_generator_from_xml_file = Test.xml_generator_from_xml_file

        self.global_ns = Test.global_ns

    def test(self):
        """
        Check the comment parsing
        """
        if self.config.castxml_epic_version != 1:
            # Run this test only with castxml epic version == 1
            return
        # Try to capture CastXML's patch version: 0.3.<###>
        # If the version is <= 0.3.6, return as the functionality doesn't exist
        # Else, continue on with the test.
        rtn = subprocess.run(
            [self.config.xml_generator_path, "--version"],
            stdout=subprocess.PIPE
        )
        version_regex = re.compile(
            b"castxml version 0.3.(?P<patch_ver>[0-9]+)"
        )
        reg_match = re.match(version_regex, rtn.stdout)
        if reg_match:
            if int(reg_match.group("patch_ver")) <= 6:
                return
        tnamespace = self.global_ns.namespace("comment")

        self.assertIn("comment", dir(tnamespace))
        self.assertEqual(["//! Namespace Comment",
                          "//! Across multiple lines"],
                         tnamespace.comment.text)

        tenumeration = tnamespace.enumeration("com_enum")
        self.assertIn("comment", dir(tenumeration))
        self.assertEqual(['/// Outside Class enum comment'],
                         tenumeration.comment.text)

        tclass = tnamespace.class_("test")
        self.assertIn("comment", dir(tclass))
        self.assertEqual(["/** class comment */"], tclass.comment.text)

        tcls_enumeration = tclass.enumeration("test_enum")
        self.assertIn("comment", dir(tcls_enumeration))
        self.assertEqual(['/// inside class enum comment'],
                         tcls_enumeration.comment.text)

        tmethod = tclass.member_functions()[0]

        self.assertIn("comment", dir(tmethod))
        self.assertEqual(["/// cxx comment", "/// with multiple lines"],
                         tmethod.comment.text)

        tconstructor = tclass.constructors()[0]

        self.assertIn("comment", dir(tconstructor))
        self.assertEqual(["/** doc comment */"], tconstructor.comment.text)

        for indx, cmt in enumerate(['//! mutable field comment',
                                    "/// bit field comment"]):
            tvariable = tclass.variables()[indx]
            self.assertIn("comment", dir(tvariable))
            self.assertEqual([cmt], tvariable.comment.text)


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite


def run_suite():
    unittest.TextTestRunner(verbosity=2).run(create_suite())


if __name__ == "__main__":
    run_suite()
