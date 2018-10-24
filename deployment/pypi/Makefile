## Colorful output
_INFO := $(shell echo -e '\e[1;36m')
_WARNING := $(shell echo -e '\e[1;33m')
_END := $(shell echo -e '\e[0m')
CWD := $(PWD)/

.PHONY: build
build:
	python3 -m pip install --user --upgrade setuptools wheel
	wget https://nodejs.org/dist/v11.0.0/node-v11.0.0-linux-x64.tar.xz
	tar xf node-v11.0.0-linux-x64.tar.xz
	cp $(CWD)../../README.md $(CWD)
	cd $(CWD)../../src/nni_manager && yarn && yarn build
	cd $(CWD)../../src/nni_manager/dist && yarn --prod
	cd $(CWD)../../src/webui && yarn && yarn build
	rm -rf $(CWD)system
	cp -r $(CWD)../../src/nni_manager/dist $(CWD)system
	cp -r $(CWD)../../src/webui/build $(CWD)system/static
	cp $(CWD)../../src/nni_manager/package.json $(CWD)system
	rm -rf $(CWD)nnicmd
	rm -rf $(CWD)nni_annotation
	cp -r $(CWD)../../tools/nnicmd $(CWD)nnicmd
	cp -r $(CWD)../../tools/nni_annotation $(CWD)nni_annotation
	cd $(CWD) && python3 setup.py bdist_wheel
	cd $(CWD)../../src/sdk/pynni && python3 setup.py bdist_wheel
	cp -r $(CWD)../../src/sdk/pynni/dist/*.whl $(CWD)dist

.PHONY: upload
upload:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*