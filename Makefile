buildup:
	docker build -t first-website . && docker run -p 80:80 -t first-website
test: 
	docker build -t test-first-website . && docker run test-first-website sh -c 'cd src; python -m coverage run -m --omit=*tests* pytest tests; python -m coverage report -m --omit=*tests*;'
