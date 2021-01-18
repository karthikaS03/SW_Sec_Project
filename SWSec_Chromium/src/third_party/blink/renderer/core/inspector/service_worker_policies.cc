#include "third_party/blink/renderer/core/inspector/service_worker_policies.h"



// :: Forensics ::
#include "third_party/blink/renderer/core/inspector/forensics.h"
//


namespace blink
{
    bool ServiceWorkerPolicies::is_policy_initialized=false;
    // std::vector<std::unique_ptr<JSONObject>> ServiceWorkerPolicies::sw_policies ;

    ServiceWorkerPolicies::ServiceWorkerPolicies() = default;
        
    ServiceWorkerPolicies::~ServiceWorkerPolicies() = default;

    //static
    std::unique_ptr<JSONObject> ServiceWorkerPolicies::GetPolicy(String& name){

        auto policy = std::make_unique<JSONObject>();
        policy->SetString("name", "notification-count");
        policy->SetString("type","Integer");

        if (name=="notification-count"){
            return policy;
        }

        return std::unique_ptr<JSONObject>();
    }

    //static
    std::vector<std::unique_ptr<JSONObject>> ServiceWorkerPolicies::InitiatePolicies(){

        std::vector<std::unique_ptr<JSONObject>> sw_policies_temp;

        std::unique_ptr<JSONObject> policy = std::make_unique<JSONObject>();
        policy->SetString("name", "notification-count-per-hour");
        policy->SetString("type","Integer");
        policy->SetInteger("value",3);             

        sw_policies_temp.push_back(std::move(policy));  

        policy = std::make_unique<JSONObject>();
        policy->SetString("name", "requests-count");
        policy->SetString("type","Integer");
        policy->SetInteger("value",20);   
        sw_policies_temp.push_back(std::move(policy));  
        
        return sw_policies_temp;   
        
    }

    //static
    bool ServiceWorkerPolicies::CheckPolicy(const String& name, String value){

        
        std::vector<std::unique_ptr<JSONObject>> sw_policies_temp = InitiatePolicies();        
        for (const auto& policy_obj: sw_policies_temp ) {
            // String* str_name = nullptr; 
            // bool res  = policy_obj->GetString(name, str_name);
            //String json = policy_obj->ToJSONString();
            JSONValue* json_value = policy_obj->Get(name);
            String value;
            json_value->AsString(&value);
  
            // if (res)
                Forensics::DebugInfo(TRACE(1), value);                                  
        }
        return true;
    }
}