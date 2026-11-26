# Deployment Fix Notes — Revision 2

The latest deployment log exposed two remaining source-format issues, plus an important missing dependency.

1. Custom Metadata record XML used `xsi:type="xsd:string"` and similar values without declaring the `xsd` namespace. The `xmlns:xsd` declaration is now present.
2. Apex class sidecar files used `.cls.meta.xml`; Salesforce DX source format requires `.cls-meta.xml`. All class sidecars were renamed, including `DisneyAgentController.cls-meta.xml`.
3. The Custom Metadata Type object definitions did not include their field definitions. Added all fields referenced by Apex and the metadata records under each type's `fields` directory.

Deploy from the `salesforce` folder:

```powershell
sf project deploy start --target-org DisneyDev --source-dir force-app
```

If a new deployment error appears, share the complete component failure table. This package has been XML-parsed locally; only the target Salesforce org can confirm metadata validation and Apex compilation.
