#ifndef THIRD_PARTY_BLINK_RENDERER_CORE_INSPECTOR_SERVICEWORKERPOLICIES_H_
#define THIRD_PARTY_BLINK_RENDERER_CORE_INSPECTOR_SERVICEWORKERPOLICIES_H_


#include "third_party/blink/renderer/core/core_export.h"

#include "third_party/blink/renderer/platform/json/json_values.h"

namespace blink {

class JSONObject;

class CORE_EXPORT ServiceWorkerPolicies {


public:
    ServiceWorkerPolicies();

    static std::unique_ptr<JSONObject> GetPolicy(String& name);

    static bool CheckPolicy(const String& name, String value);

    static std::vector<std::unique_ptr<JSONObject>> InitiatePolicies();

    ~ServiceWorkerPolicies();
     
    static std::vector<std::unique_ptr<JSONObject>> sw_policies;
    static bool is_policy_initialized;

    
};



} // namespace blink

#endif // !defined(ServiceWorkerPolicies_h)