{ lib
, python3Packages
}:

with python3Packages;
buildPythonPackage rec {
  pname = "python-rsync-filter";
  version = "2024.1.9";
  format = "pyproject";

  src = ./.;

  nativeBuildInputs = [
    hatchling
  ];

  propagatedBuildInputs = [
    pytest
  ];

  nativeCheckInputs = [
    pytestCheckHook
  ];

  meta = with lib; {
    description = pname;
    homepage = "https://github.com/presto8/python-rsync-filter";
    license = licenses.asl20;
    maintainers = with maintainers; [ presto8 ];
  };
}
