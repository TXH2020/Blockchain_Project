from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files import File
import os

def encrypt_file(paper):

	key = Fernet.generate_key()
	input_file = paper
	output_file = os.path.join(settings.ENCRYPTION_ROOT,str(paper)+'.encrypted')

	data = input_file.read()

	fernet = Fernet(key)
	encrypted = fernet.encrypt(data)

	with open(output_file, 'wb') as f:
	    f.write(encrypted) 

	return key


def decrypt_file(paper,key,s_code):
	
	fernet = Fernet(key)
	paper = paper.text.encode('utf-8')

	decrypted = fernet.decrypt(paper)
	
	with open('media/'+s_code+'.pdf','wb') as f:
		f.write(decrypted)

	file_ = open('media/'+s_code+'.pdf','rb')
	f_file = File(file_)

	return f_file