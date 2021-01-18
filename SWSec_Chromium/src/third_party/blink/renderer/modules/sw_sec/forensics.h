#ifndef THIRD_PARTY_BLINK_RENDERER_MODULE_INSPECTOR_FORENSICS_H_
#define THIRD_PARTY_BLINK_RENDERER_MODULE_INSPECTOR_FORENSICS_H_

#include "third_party/blink/renderer/core/core_export.h"
#include "v8/include/v8.h"
#include "third_party/blink/renderer/platform/wtf/text/text_position.h"
#include "third_party/blink/renderer/core/loader/frame_loader_types.h"
#include "third_party/blink/renderer/core/dom/document.h"
// #include "third_party/blink/public/mojom/notifications/notification_service.mojom-blink.h"
// #include "third_party/blink/public/mojom/notifications/notification.mojom-blink-forward.h"
#include "third_party/blink/public/mojom/notifications/notification.mojom-blink.h"
#include "third_party/blink/renderer/modules/notifications/notification.h"
#include "third_party/blink/renderer/platform/wtf/text/string_builder.h"
#include "third_party/blink/renderer/core/html/parser/text_resource_decoder.h"

#include "third_party/blink/renderer/modules/service_worker/service_worker_registration.h"
#include "third_party/blink/renderer/modules/service_worker/service_worker.h"
#include "third_party/blink/renderer/modules/service_worker/service_worker_global_scope.h"
#include "third_party/blink/renderer/core/inspector/forensics.h"

#ifndef TRACING
#define TRACE_SW(is_log) blink::ForensicsModule::TRACE_FUNC_INFO(is_log, __func__, __FILE__, __LINE__)
#endif 



namespace blink {

class Frame;
class ChromeClient;
class Node;
class ExecutionContext;
class WebThread;
class V8EventListener;
class ScriptSourceCode;
class ScriptState;
class EventTarget;
class SerializedScriptValue;
class DOMWindow;
class LocalDOMWindow;
class Event;
class KURL;
class Notification;
class ServiceWorkerRegistration;
class ServiceWorkerGlobalScope;
class Forensics;


struct WebWindowFeatures;

using ArgNameValPair = std::pair<std::string,v8::Local<v8::Value>>;
using ArgNameListenerPair = std::pair<std::string,V8EventListener*>;

class MODULES_EXPORT ForensicsModule  
                                        // : public Forensics   
                                        {
  int WTF_MAKE_NONCOPYABLE(ForensicsModule);

  public:
  
//   ForensicsModule();

//   ~ForensicsModule();

  friend class Forensics;

  static void LogInfo(std::string log_str);

  static std::string TRACE_FUNC_INFO(bool is_log, 
                                     std::string const& fun, 
                                     std::string const& file, 
                                     int const line);
  

  static void LogSWInfo(std::string const& func_info, 
                        ExecutionContext* execution_context, 
                        const KURL& url);

  static void LogSWInfo(std::string const& func_info, 
                        const String sw_url, 
                        const KURL& url);

  static void LogSWEvent(std::string const& func_info, 
                          const int event_id);

  static void LogNotificationData(std::string const& func_info, 
                                  ExecutionContext* context,
                                  mojom::blink::NotificationDataPtr data,                                  
                                  const String& notification_id);

  static void DidCallFunction(  std::string func_state,
                                ExecutionContext* execution_context,
                                v8::Local<v8::Function> function,
                                v8::Local<v8::Value> receiver,
                                std::vector<v8::Local<v8::Value>> args);
  
  static void DidCompileScript(LocalFrame* frame, 
                              const ScriptSourceCode& source, const int scriptID);
  
  static void DebugInfo(std::string const& func_info, 
                          const String debug_info );
    
  static void DebugInfo(std::string const& func_info, 
                          const int debug_info );
  
  static void DebugInfo(std::string const& func_info, ExecutionContext* execution_context,
                          const String debug_info );

  static void AppendResponseData(const char* buffer, size_t available);

  static void LogFetchResponse(std::string const& func_info, 
                          ScriptPromise promise, 
                          ScriptState* script_state);

  static StringBuilder builder_;        

  static void LogSWContextInfo(std::string const& func_info,
                                ExecutionContext* execution_context,                                  
                                const KURL& url, const String& data);
  private:
    

    struct V8FunctionFeatures {
        int scriptID = 0;
        int line = 0;
        int column = 0; 
        std::string debug_name;
        std::string url;
    };

    static std::string V8ValueToString(
                                        v8::Local<v8::Value> v8Value);

    static V8FunctionFeatures TranslateV8Function(                                         
                                                 v8::Local<v8::Function> function);

    static Document* GetDocument(LocalFrame* frame);
    static String GetDocumentURL(LocalFrame* frame);
    static LocalFrame* GetFrameRoot(LocalFrame* frame);
    static String GetFrameRootURL(LocalFrame* frame);
    static Frame* GetMainFrame(LocalFrame* frame);
    
};


} // namespace blink

#endif // !defined(Forensics_h)

