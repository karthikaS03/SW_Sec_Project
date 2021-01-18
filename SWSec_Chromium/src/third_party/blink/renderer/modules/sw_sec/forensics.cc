#include "third_party/blink/renderer/modules/sw_sec/forensics.h"

#include "third_party/blink/renderer/core/page/chrome_client.h"
#include "third_party/blink/renderer/core/dom/node.h"
#include "third_party/blink/renderer/core/dom/element.h"
#include "third_party/blink/renderer/core/dom/events/event.h"
#include "third_party/blink/renderer/core/html/html_script_element.h"
#include "third_party/blink/renderer/core/editing/serializers/serialization.h"
#include "third_party/blink/renderer/core/page/page.h"
#include "third_party/blink/renderer/core/frame/local_frame.h"
// #include "third_party/blink/renderer/core/execution_context/execution_context.h"
#include "third_party/blink/renderer/core/html_names.h"
#include "v8/include/v8.h"
#include "third_party/blink/renderer/bindings/core/v8/source_location.h"
#include "third_party/blink/renderer/bindings/core/v8/script_source_code.h"
#include "third_party/blink/renderer/bindings/core/v8/script_function.h"
#include "third_party/blink/renderer/bindings/core/v8/script_promise.h"
#include "third_party/blink/renderer/core/workers/worker_or_worklet_global_scope.h"
#include "third_party/blink/renderer/core/workers/worker_thread.h"
#include "third_party/blink/renderer/core/dom/document.h"
#include "third_party/blink/renderer/core/frame/local_dom_window.h"
#include "third_party/blink/renderer/core/frame/local_frame.h"

#include <sstream>

#define _IFA_DISABLE_ // return;

#define _IFAC_ "LOG::Forensics"
#define _IFAF_ __func__
#define _IFA_LOG_SPACE_ "\n  -*#$"
#define _IFA_ANDROID_LOGCAT_

#define _IFA_LOG_PREFIX_  _IFAC_ << "::" << _IFAF_ << " :"
#define _IFA_LOG_SUFFIX_  "\n---***###$$$\n"

#define _IFA_LOG_FRAME_  _IFA_LOG_SPACE_ << "frame=" << frame \
          << _IFA_LOG_SPACE_ << "frame_url=" \
              << GetDocumentURL(frame).Utf8().data() \
          << _IFA_LOG_SPACE_ << "main_frame=" << GetMainFrame(frame) \
          << _IFA_LOG_SPACE_ << "local_frame_root=" \
              << GetFrameRoot(frame) \
          << _IFA_LOG_SPACE_ << "local_frame_root_url=" \
              << GetFrameRootURL(frame) \
          << _IFA_LOG_SPACE_ << "document=" << (void*)GetDocument(frame)


namespace blink {

using std::string;

// ForensicsModule::ForensicsModule(){}

// ForensicsModule::~ForensicsModule() = default;

//static
Document* ForensicsModule::GetDocument(LocalFrame* frame) {
  if(!frame)
      return nullptr;

  return frame->GetDocument();
}


//static
String ForensicsModule::GetDocumentURL(LocalFrame* frame) {
  if(!frame || !frame->GetDocument())
      return KURL().GetString();

  return frame->GetDocument()->Url().GetString();
}

//static
LocalFrame* ForensicsModule::GetFrameRoot(LocalFrame* frame) {
  if(!frame)
      return nullptr;

  return &(frame->LocalFrameRoot());
}

//static
String ForensicsModule::GetFrameRootURL(LocalFrame* frame) {
  if(!frame)
      return KURL().GetString();

  return GetDocumentURL(GetFrameRoot(frame));
}

//static
Frame* ForensicsModule::GetMainFrame(LocalFrame* frame) {
  if(!frame || !frame->GetDocument() || !frame->GetDocument()->GetPage())
      return nullptr;

  return frame->GetDocument()->GetPage()->MainFrame();
}



//static
void ForensicsModule::LogInfo(std::string log_str) {
  // Write log that can be read via adb logcat
  LOG(INFO) << log_str;
  
}

//static
std::string ForensicsModule::TRACE_FUNC_INFO(bool is_log, std::string const& fun, std::string const& file, int const line) {
  
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

//static
void ForensicsModule::LogSWInfo(std::string const& func_info, 
                          ExecutionContext* execution_context, 
                          const KURL& url){  
  LocalFrame* frame;
  
  if (execution_context->IsServiceWorkerGlobalScope()){
    LogSWContextInfo(func_info, execution_context, url, "");
    return;
  }
  if(execution_context->IsDocument())
      frame = To<LocalDOMWindow>(execution_context)->GetFrame();
  else
    return;
  
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "is_service_worker=" << execution_context->IsServiceWorkerGlobalScope()
          << _IFA_LOG_SPACE_  << "is_document=" << execution_context->IsDocument()
          << _IFA_LOG_FRAME_  
          << _IFA_LOG_SPACE_  << "context_url=" << execution_context->Url().GetString() 
          << _IFA_LOG_SPACE_  << "request_url=" << url.GetString().Utf8().data()
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::LogSWInfo(std::string const& func_info, 
                          const String sw_info, 
                          const KURL& url){
   
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "sw_info=" << sw_info
          << _IFA_LOG_SPACE_  << "request_url=" << url.GetString().Utf8().data()
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::LogSWEvent(std::string const& func_info, 
                          const int event_id){

  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "event_id=" << event_id
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

void ForensicsModule::LogSWContextInfo(std::string const& func_info,
                                ExecutionContext* execution_context,                                 
                                const KURL& url,  const String& data){
  
          
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info          
          << _IFA_LOG_SPACE_  << "is_service_worker="  << IsA<ServiceWorkerGlobalScope>(execution_context)
          << _IFA_LOG_SPACE_  << "script_url="         << To<ServiceWorkerGlobalScope>(execution_context)->serviceWorker()->scriptURL()
          << _IFA_LOG_SPACE_  << "scope="              << To<ServiceWorkerGlobalScope>(execution_context)->registration()->scope()
          << _IFA_LOG_SPACE_  << "scope_name="         << To<ServiceWorkerGlobalScope>(execution_context)->InterfaceName()
          << _IFA_LOG_SPACE_  << "registration_id="    << To<ServiceWorkerGlobalScope>(execution_context)->registration()->RegistrationId()
          << _IFA_LOG_SPACE_  << "worker_id="          << (To<WorkerOrWorkletGlobalScope>(execution_context))->GetThread()->GetPlatformThreadId()
          << _IFA_LOG_SPACE_  << "service_worker_url=" << execution_context->Url().GetString() 
          << _IFA_LOG_SPACE_  << "request_url="        << url.GetString().Utf8().data()
          << _IFA_LOG_SPACE_  << "data="               << data.Utf8().data()
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::LogNotificationData(std::string const& func_info, 
                                    ExecutionContext* execution_context,
                                    mojom::blink::NotificationDataPtr notification_data,                                     
                                    const String& notification_id){


  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "is_service_worker=" << execution_context->IsServiceWorkerGlobalScope()
          << _IFA_LOG_SPACE_  << "context_url=" << execution_context->Url().GetString() 
          << _IFA_LOG_SPACE_  << "notification_id=" << notification_id
          << _IFA_LOG_SPACE_  << "notification_title=" << notification_data->title
          << _IFA_LOG_SPACE_  << "notification_tag=" << notification_data->tag
          << _IFA_LOG_SPACE_  << "notification_body=" << notification_data->body
          << _IFA_LOG_SPACE_  << "notification_image=" << notification_data->image.GetString()
          << _IFA_LOG_SPACE_  << "notification_icon=" << notification_data->icon.GetString()
          << _IFA_LOG_SPACE_  << "notification_badge=" << notification_data->badge.GetString()
          << _IFA_LOG_SUFFIX_;

  LogInfo(log_str.str());
  
}

// Called when a script has been compiled
// and right before being executed
void ForensicsModule::DidCompileScript(
        LocalFrame* frame, 
        const ScriptSourceCode& source,
        const int scriptID) {

  _IFA_DISABLE_

  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_
          << _IFA_LOG_FRAME_
          << _IFA_LOG_SPACE_ << "scriptID=" << scriptID
          << " (" << source.StartPosition().line_.OneBasedInt() 
          << "," << source.StartPosition().column_.OneBasedInt() << ")"
          << _IFA_LOG_SPACE_ << "url=" << source.Url().GetString().Utf8().data()
          << _IFA_LOG_SPACE_ << "code=" << source.Source().ToString().Utf8().data()
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}


// static
void ForensicsModule::DidCallFunction(std::string func_state,
                                ExecutionContext* execution_context,
                                v8::Local<v8::Function> function,
                                v8::Local<v8::Value> receiver,
                                std::vector<v8::Local<v8::Value>> args) {

  V8FunctionFeatures func_feat = TranslateV8Function(function);
  
  if(!execution_context->IsServiceWorkerGlobalScope())
    return ;

  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_          
          << _IFA_LOG_SPACE_  << "is_service_worker="  << IsA<ServiceWorkerGlobalScope>(execution_context)
          << _IFA_LOG_SPACE_  << "script_url="         << To<ServiceWorkerGlobalScope>(execution_context)->serviceWorker()->scriptURL()
          << _IFA_LOG_SPACE_  << "scope="              << To<ServiceWorkerGlobalScope>(execution_context)->registration()->scope()
          << _IFA_LOG_SPACE_  << "registration_id="    << To<ServiceWorkerGlobalScope>(execution_context)->registration()->RegistrationId()
          << _IFA_LOG_SPACE_  << "worker_id="          << (To<WorkerOrWorkletGlobalScope>(execution_context))->GetThread()->GetPlatformThreadId()
          << _IFA_LOG_SPACE_  << "func_name="          << func_state
          << _IFA_LOG_SPACE_  << "scriptID="           << func_feat.scriptID << " (" << func_feat.line << "," << func_feat.column << ")"
          << _IFA_LOG_SPACE_  << "callback_debug_name=" << func_feat.debug_name
          << _IFA_LOG_SPACE_  << "script_url="         << func_feat.url;

 

  for(auto a : args) {
    log_str << _IFA_LOG_SPACE_ 
            << "arg_value=" << V8ValueToString( a);
  }

  log_str << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}


// static
std::string ForensicsModule::V8ValueToString(
                                        v8::Local<v8::Value> v8Value) {

  std::string valueStr;


  if(v8Value.IsEmpty())
    return valueStr;

  if(v8Value->IsNull()) {
    valueStr += "<=V8 VALUE NULL=>";
    return valueStr;
  }

  if(v8Value->IsNullOrUndefined()) {
    valueStr += "<=V8 VALUE UNDEFINED=>";
    return valueStr;
  }

  if(v8Value->IsFunction()) {
    V8FunctionFeatures ff = TranslateV8Function(v8Value.As<v8::Function>());
    valueStr += "<=V8 FUNCTION=> scriptID=";
    valueStr += std::to_string(ff.scriptID);
    valueStr += " (";
    valueStr += std::to_string(ff.line);
    valueStr += ",";
    valueStr += std::to_string(ff.column);
    valueStr += ") ";
    valueStr += ff.debug_name;
    return valueStr;
  }

  if(v8Value->IsObject()) {
    valueStr += "<=V8 OBJECT=>";
  }

  return valueStr;

}

// static
ForensicsModule::V8FunctionFeatures ForensicsModule::TranslateV8Function(                                         
                                            v8::Local<v8::Function> function) {

  V8FunctionFeatures func_feat;

  v8::Local<v8::Function> original_function = GetBoundFunction(function);
  v8::Local<v8::Value> function_name = original_function->GetDebugName();

  if (!function_name.IsEmpty() && function_name->IsString()) {
    
             func_feat.debug_name = (ToCoreString(function_name.As<v8::String>())).Utf8().data();
  }
  else {
    function_name = function->GetDebugName();
    if(!function_name.IsEmpty() && function_name->IsString())    
             func_feat.debug_name = (ToCoreString(function_name.As<v8::String>())).Utf8().data();
  }

  std::unique_ptr<SourceLocation> location = SourceLocation::FromFunction(original_function);
    
  func_feat.scriptID = location->ScriptId();
  func_feat.url = location->Url().Utf8().data();
  func_feat.line = location->LineNumber();
  func_feat.column =  location->ColumnNumber();
  
  return func_feat;

}

//static
void ForensicsModule::DebugInfo(std::string const& func_info, 
                          const String debug_info ){
      
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "debug_text=" << debug_info          
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::DebugInfo(std::string const& func_info, ExecutionContext* execution_context,
                          const String debug_info ){
      
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "context_url=" << execution_context->Url().GetString() 
          << _IFA_LOG_SPACE_  << "debug_text=" << debug_info          
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::DebugInfo(std::string const& func_info,
                          const int debug_info ){
      
  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_ 
          << func_info         
          << _IFA_LOG_SPACE_  << "debug_num=" << debug_info          
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}


//static 
void ForensicsModule::LogFetchResponse(std::string const& func_info, 
                          ScriptPromise promise, 
                          ScriptState* script_state){
      
  std::ostringstream log_str;
  ScriptValue on_rejected, on_fulfilled;
  String result ;

  // promise.Then(FunctionForScriptPromiseTest::CreateFunction(
  //                  script_state, &on_fulfilled),
  //              FunctionForScriptPromiseTest::CreateFunction(
  //                  script_state, &on_rejected));

  // v8::MicrotasksScope::PerformCheckpoint(script_state->GetIsolate());

  if (on_fulfilled.IsEmpty() || on_fulfilled.IsNull() || on_fulfilled.IsUndefined())
    result = "no data";
  else
    result = "not empty";
  // ToCoreString(v8::Local<v8::String>::Cast(on_fulfilled.V8Value()));


  log_str << _IFA_LOG_PREFIX_ 
          << func_info
          << _IFA_LOG_SPACE_  << "debug_text=" << result          
          << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

//static
void ForensicsModule::AppendResponseData(const char* buffer, size_t available){
  StringBuilder builder_;
  
  std::unique_ptr<TextResourceDecoder> decoder_;
  if (available > 0)
  {
    builder_.Append(decoder_->Decode(buffer, available));
  }
  else
  {
    builder_.Append(decoder_->Flush());
    std::ostringstream log_str;
    log_str << _IFA_LOG_PREFIX_           
          << _IFA_LOG_SPACE_  << "response_data=" << builder_.ToString()         
          << _IFA_LOG_SUFFIX_;
    LogInfo(log_str.str());
    builder_.Clear();
  }
  
}

/* For Future Use
//static
bool ForensicsModule::IsWhitespace(Node* node) {
  // TODO: pull ignoreWhitespace setting from the frontend and use here.
  return node && node->getNodeType() == Node::kTextNode &&
         node->nodeValue().StripWhiteSpace().length() == 0;
}

void ForensicsModule::DidInsertDOMNode(Node* node) {

  _IFA_DISABLE_

  if (IsWhitespace(node))
    return;

  if(!node || !node->GetDocument().GetFrame())
    return;

  LocalFrame* frame = node->GetDocument().GetFrame();

  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_
          << _IFA_LOG_FRAME_
          << _IFA_LOG_SPACE_ << "parent_ptr=" << (void*)(node->parentNode())
          << _IFA_LOG_SPACE_ << "prev_sibling_ptr=" << (void*)(node->previousSibling())
          << _IFA_LOG_SPACE_ << "next_sibling_ptr=" << (void*)(node->nextSibling())
          << _IFA_LOG_SPACE_ << "node_ptr=" << (void*)node
          << _IFA_LOG_SPACE_ << "node=" << node;
  
  Element* element = nullptr; 
  if(node->IsHTMLElement())
    // element = dynamic_cast<Element*>(node);
    element = (Element*)node;

  if(!element) {
    log_str << _IFA_LOG_SUFFIX_;
    LogInfo(log_str.str());
    return;
  }

  if(element->IsLink()) {
    log_str << _IFA_LOG_SPACE_ << "node_href=" 
            << element->HrefURL().GetString().Utf8().data();
  }
  else if(element->IsScriptElement()) {
    String src_attr = element->getAttribute(html_names::kSrcAttr).GetString();
    log_str << _IFA_LOG_SPACE_ << "src_url=" << src_attr.Utf8().data();
  }

  log_str << _IFA_LOG_SUFFIX_;
  LogInfo(log_str.str());
}

void ForensicsModule::WillRemoveDOMNode(Node* node) {

  _IFA_DISABLE_

  if (IsWhitespace(node))
    return;
  
  if(!node || !node->GetDocument().GetFrame())
    return;

  LocalFrame* frame = node->GetDocument().GetFrame();

  std::ostringstream log_str;
  log_str << _IFA_LOG_PREFIX_
          << _IFA_LOG_FRAME_
          << _IFA_LOG_SPACE_ << "parent_ptr=" << (void*)(node->parentNode())
          << _IFA_LOG_SPACE_ << "prev_sibling_ptr=" << (void*)(node->previousSibling())
          << _IFA_LOG_SPACE_ << "next_sibling_ptr=" << (void*)(node->nextSibling())
          << _IFA_LOG_SPACE_ << "node_ptr=" << (void*)node
          << _IFA_LOG_SPACE_ << "node=" << node
          << _IFA_LOG_SUFFIX_;
  // TODO(Roberto): add full markup?
  // LogInfo(log_str.str());
}

*/

} // namespace blink