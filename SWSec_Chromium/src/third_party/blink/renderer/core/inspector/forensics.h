#ifndef THIRD_PARTY_BLINK_RENDERER_CORE_INSPECTOR_FORENSICS_H_
#define THIRD_PARTY_BLINK_RENDERER_CORE_INSPECTOR_FORENSICS_H_

#include "third_party/blink/renderer/core/core_export.h"
#include "v8/include/v8.h"
#include "third_party/blink/renderer/platform/wtf/text/text_position.h"
#include "third_party/blink/renderer/core/loader/frame_loader_types.h"
#include "third_party/blink/renderer/core/dom/document.h"
// #include "third_party/blink/public/mojom/notifications/notification_service.mojom-blink.h"
// #include "third_party/blink/public/mojom/notifications/notification.mojom-blink-forward.h"
#include "third_party/blink/public/mojom/notifications/notification.mojom-blink.h"
#include "third_party/blink/renderer/platform/wtf/text/string_builder.h"
#include "third_party/blink/renderer/core/html/parser/text_resource_decoder.h"
#include "third_party/blink/renderer/modules/sw_sec/forensics.h"

#include "chrome/browser/task_manager/task_manager_interface.h"
#include "chrome/common/extensions/api/processes.h"
#include "chrome/browser/sw_forensics/sw_forensics.h"
#include "third_party/blink/public/mojom/timing/resource_timing.mojom-blink.h"

#ifndef TRACING


#define _IFAC_ "LOG::Forensics"
#define _IFAF_ __func__
#define _IFA_LOG_SPACE_ "\n  -*#$"
#define _IFA_ANDROID_LOGCAT_

#define _IFA_LOG_PREFIX_  _IFAC_ << "::" << _IFAF_ << " :"
#define _IFA_LOG_SUFFIX_  "\n---***###$$$\n"


#define TRACE(is_log) blink::Forensics::TRACE_FUNC_INFO(is_log, __func__, __FILE__, __LINE__)
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
class Page;
class ForensicsModule;
class TaskManagerInterface;

struct WebWindowFeatures;

using ArgNameValPair = std::pair<std::string,v8::Local<v8::Value>>;
using ArgNameListenerPair = std::pair<std::string,V8EventListener*>;

class CORE_EXPORT Forensics {
//   int WTF_MAKE_NONCOPYABLE(Forensics);

  public:
//   Forensics();
  
//   ~Forensics();
  

  static void LogInfo(std::string log_str){
      // Write log that can be read via adb logcat
      LOG(INFO) << log_str;  
  }
  
  static void CreateDocument(std::string const& func_info, Document* document );

  static void CloseDocument(std::string const& func_info, Document* document );

  static void GetSWUsageInfo(int version_id);

  static std::string TRACE_FUNC_INFO(bool is_log, 
                                     std::string const& fun, 
                                     std::string const& file, 
                                     int const line){
      std::ostringstream log_str;
                
      if(is_log)
      {
        log_str << _IFA_LOG_PREFIX_;
      }
      log_str << _IFA_LOG_SPACE_ << "func_name=" << fun
              << _IFA_LOG_SPACE_ << "file_name=" << file
              << _IFA_LOG_SPACE_ << "line_number=" << line;
      if(is_log)
      {
        log_str << _IFA_LOG_SUFFIX_;
        LogInfo(log_str.str());
      }
      
      return log_str.str();
  }
  

  static void LogSWInfo(std::string const& func_info, 
                        ExecutionContext* execution_context, 
                        const KURL& url);

  static void LogSWInfo(std::string const& func_info, 
                        const String sw_url, 
                        const KURL& url);

  static void LogPermissionInfo(std::string const& func_info, 
                        // const String sw_url, 
                        const GURL& url);

  static void LogSWEvent(std::string const& func_info, 
                          const int event_id);

  static void LogNotificationData(std::string const& func_info, 
                                  ExecutionContext* context,
                                  mojom::blink::NotificationDataPtr data,                                  
                                  const String& notification_id);

  static void LogNotificationEvent(std::string const& func_info, 
                                  std::string const& notification_id, 
                                  const GURL& origin_url,
                                  const base::string16& display_source);

  static void LogTaskUsageInfo(std::string const& func_info, 
                                 const base::string16 title,
                                 sw_forensics::Process* process);

  static void LogResourceTiming(std::string const& func_info,
                                ExecutionContext* execution_context,
                                mojom::blink::ResourceTimingInfoPtr resource);

  static void  DidCallFunction(std::string func_state,
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
                                const KURL& url);
  
  static bool listener_added;

  static bool HasListener();

  static void SetListener();

  
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

