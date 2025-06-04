import logging

# Logger नाव ठेवा
logger = logging.getLogger("myapp_logger")
logger.setLevel(logging.DEBUG)  # सर्व प्रकारचे logs (debug आणि त्याहून वरचे)

# Console साठी handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# File साठी handler
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Logging message चा format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Logger मध्ये handlers add करा
logger.addHandler(console_handler)
logger.addHandler(file_handler)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user_system")
