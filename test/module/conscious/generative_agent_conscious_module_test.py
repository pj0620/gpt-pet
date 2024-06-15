import os
import unittest

from dotenv import load_dotenv

from module.conscious.generative_agent_conscious_module import GenerativeAgentConsciousModule


class TestGenerativeAgentConsciousModule(unittest.TestCase):
  
  def setUp(self):
    load_dotenv(dotenv_path='test/.env', verbose=True)
    #
    # self.conscious_module = GenerativeAgentConsciousModule(
    #   VectorDBAdapterService()
    # )
  
  def test_upper(self):
    self.assertEqual('foo'.upper(), 'FOO')