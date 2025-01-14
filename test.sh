mkdir media
coverage run --source chatHLB_backend,user,utils,task,bank -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage report
rm -r media
exit $ret