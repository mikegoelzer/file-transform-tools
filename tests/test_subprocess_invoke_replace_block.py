import os
import subprocess
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_helpers import TestHelpersMixin

class TestSubprocessInvokeReplaceBlock(unittest.TestCase, TestHelpersMixin):
    def test_subprocess_invoke_prepend(self):
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp.write("A\nB\nC\n")
        temp.close()
        try:
            p = subprocess.run(["replace-block", "-y", "-b", "-r", f"@{temp.name}", "-pat", "bash_rc_export_path", "-P", "-o", "outfile.txt", "-w", "3", "2", "readme.md"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = p.stdout.decode('utf-8')
            stderr = p.stderr.decode('utf-8')
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            print(f"returncode: {p.returncode}")

            self.fail("finish TODOs here")

            if os.path.exists("outfile.txt"):
                with open("outfile.txt", "r") as f:
                    output_contents = f.read()
                print(f"outfile.txt contents:\n{output_contents}")
                # TODO: assert correct output here
                #self.assertTrue(output_contents == "\n\n\nA\nB\nC\n", "Output file should not be empty")
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.returncode}")
            print(f"stdout: {e.stdout.decode('utf-8')}")
            print(f"stderr: {e.stderr.decode('utf-8')}")
            raise e
        finally:
            if os.path.exists("outfile.txt"):
                os.unlink("outfile.txt")
            if os.path.exists(temp.name):
                os.unlink(temp.name)

    def test_subprocess_invoke_append(self):
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp.write("A\nB\nC\n")
        temp.close()
        try:
            p = subprocess.run(["file_transform_tools/replace_block.py", "-y", "-b", "-r", f"@{temp.name}", "-pat", "bash_rc_export_path", "-A", "-o", "outfile.txt", "-w", "3", "2", "readme.md"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = p.stdout.decode('utf-8')
            stderr = p.stderr.decode('utf-8')
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            print(f"returncode: {p.returncode}")

            self.fail("finish TODOs here")

            if os.path.exists("outfile.txt"):
                with open("outfile.txt", "r") as f:
                    output_contents = f.read()
                print(f"outfile.txt contents:\n{output_contents}")
                # TODO: assert correct output here
                #self.assertTrue(output_contents == "\n\n\nA\nB\nC\n", "Output file should not be empty")
                
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.returncode}")
            print(f"stdout: {e.stdout.decode('utf-8')}")
            print(f"stderr: {e.stderr.decode('utf-8')}")
            raise e
        finally:
            if os.path.exists("outfile.txt"):
                os.unlink("outfile.txt")
            if os.path.exists(temp.name):
                os.unlink(temp.name)
