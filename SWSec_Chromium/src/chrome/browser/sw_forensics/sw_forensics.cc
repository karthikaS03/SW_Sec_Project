// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/sw_forensics/sw_forensics.h"

#include <stdint.h>

#include <algorithm>
#include <memory>
#include <set>
#include <utility>

#include "base/bind.h"
#include "base/lazy_instance.h"
#include "base/metrics/histogram_macros.h"
#include "base/process/process.h"
#include "base/strings/string_number_conversions.h"
#include "base/strings/utf_string_conversions.h"
#include "base/task/post_task.h"
#include "chrome/browser/extensions/api/tabs/tabs_constants.h"
#include "chrome/browser/extensions/extension_tab_util.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/browser/task_manager/task_manager_interface.h"
#include "chrome/common/extensions/api/processes.h"
#include "content/public/browser/browser_child_process_host.h"
#include "content/public/browser/browser_task_traits.h"
#include "content/public/browser/browser_thread.h"
#include "content/public/browser/child_process_data.h"
#include "content/public/browser/render_frame_host.h"
#include "content/public/browser/render_process_host.h"
#include "content/public/browser/web_contents.h"
#include "content/public/common/child_process_host.h"
#include "content/public/common/result_codes.h"
#include "extensions/common/error_utils.h"

//Forensics
#include "third_party/blink/renderer/core/inspector/forensics.h"
//

namespace sw_forensics {


TaskInfo::TaskInfo()
 {}

TaskInfo::~TaskInfo() {}
TaskInfo::TaskInfo(TaskInfo&& rhs)
: title(std::move(rhs.title)),
tab_id(std::move(rhs.tab_id)){
}


Cache::Cache()
: size(0.0),
live_size(0.0) {}

Cache::~Cache() {}
Cache::Cache(Cache&& rhs)
: size(rhs.size),
live_size(rhs.live_size){
}




Process::Process()
: id(0),
os_process_id(0),
type(PROCESS_TYPE_NONE),
nacl_debug_port(0) {}

Process::~Process() {}
Process::Process(Process&& rhs)
: id(rhs.id),
os_process_id(rhs.os_process_id),
type(rhs.type),
profile(std::move(rhs.profile)),
nacl_debug_port(rhs.nacl_debug_port),
tasks(std::move(rhs.tasks)),
cpu(std::move(rhs.cpu)),
network(std::move(rhs.network)),
private_memory(std::move(rhs.private_memory)),
js_memory_allocated(std::move(rhs.js_memory_allocated)),
js_memory_used(std::move(rhs.js_memory_used)),
sqlite_memory(std::move(rhs.sqlite_memory)),
image_cache(std::move(rhs.image_cache)),
script_cache(std::move(rhs.script_cache)),
css_cache(std::move(rhs.css_cache)){
}


namespace {


std::unique_ptr<Cache> CreateCacheData(
    const blink::WebCacheResourceTypeStat& stat) {
  std::unique_ptr<Cache> cache(new Cache());
  cache->size = static_cast<double>(stat.size);
  cache->live_size = static_cast<double>(stat.size);
  return cache;
}

ProcessType GetProcessType(
    task_manager::Task::Type task_type) {
  switch (task_type) {
    case task_manager::Task::BROWSER:
      //Forensics
      blink::Forensics::DebugInfo(TRACE(0),1);
      //
      return PROCESS_TYPE_BROWSER;

    case task_manager::Task::RENDERER:
      //Forensics
      blink::Forensics::DebugInfo(TRACE(0),2);
      //
      return PROCESS_TYPE_RENDERER;

    case task_manager::Task::EXTENSION:
    case task_manager::Task::GUEST:
      return PROCESS_TYPE_EXTENSION;

    case task_manager::Task::PLUGIN:
      return PROCESS_TYPE_PLUGIN;

    case task_manager::Task::NACL:
      return PROCESS_TYPE_NACL;

    // TODO(https://crbug.com/1048715): Assign a different process type for each
    //                                  worker type.
    case task_manager::Task::DEDICATED_WORKER:
    case task_manager::Task::SHARED_WORKER:
      return PROCESS_TYPE_WORKER;

    case task_manager::Task::SERVICE_WORKER:
      //Forensics
      blink::Forensics::DebugInfo(TRACE(0),3);
      //
      return PROCESS_TYPE_SERVICE_WORKER;

    case task_manager::Task::UTILITY:
      return PROCESS_TYPE_UTILITY;

    case task_manager::Task::GPU:
      return PROCESS_TYPE_GPU;

    case task_manager::Task::UNKNOWN:
    case task_manager::Task::ARC:
    case task_manager::Task::CROSTINI:
    case task_manager::Task::PLUGIN_VM:
    case task_manager::Task::SANDBOX_HELPER:
    case task_manager::Task::ZYGOTE:
      return PROCESS_TYPE_OTHER;
  }

  NOTREACHED() << "Unknown task type.";
  return PROCESS_TYPE_NONE;
}






// Fills |out_process| with the data of the process in which the task with |id|
// is running. If |include_optional| is true, this function will fill the
// optional fields in |extensions::api::processes::Process| except for |private_memory|,
// which should be filled later if needed.
void FillProcessData(
    task_manager::TaskId id,
    task_manager::TaskManagerInterface* task_manager,
    bool include_optional,
    Process* out_process) {
  DCHECK(out_process);
  
  const base::string16 process_title = task_manager->GetTitle(id);
  out_process->id = task_manager->GetChildProcessUniqueId(id);
  out_process->os_process_id = task_manager->GetProcessId(id);
  out_process->type = GetProcessType(task_manager->GetType(id));
  out_process->profile = base::UTF16ToUTF8(task_manager->GetProfileName(id));
  out_process->nacl_debug_port = task_manager->GetNaClDebugStubPort(id);

  // Collect the tab IDs of all the tasks sharing this renderer if any.
  const task_manager::TaskIdList tasks_on_process =
      task_manager->GetIdsOfTasksSharingSameProcess(id);
  for (const int64_t task_id : tasks_on_process) {
    TaskInfo task_info;
    //Forensics
    // blink::Forensics::LogTaskUsageInfo(TRACE(0),task_manager->GetTitle(task_id), out_process);
    // blink::Forensics::DebugInfo(TRACE(0),task_id);
    //
    task_info.task_id = std::to_string(task_id);
    task_info.title = base::UTF16ToUTF8(task_manager->GetTitle(task_id));
    const double task_cpu_usage = task_manager->GetPlatformIndependentCPUUsage(task_id);
    if (!std::isnan(task_cpu_usage))
      task_info.cpu = task_cpu_usage;//std::make_unique<double>(task_cpu_usage);
    const SessionID tab_id = task_manager->GetTabId(task_id);
    if (tab_id.is_valid())
      task_info.tab_id.reset(new int(tab_id.id()));

    out_process->tasks.push_back(std::move(task_info));
  }

  // If we don't need to include the optional properties, just return now.
  if (!include_optional)
    return;

  const double cpu_usage = task_manager->GetPlatformIndependentCPUUsage(id);
  if (!std::isnan(cpu_usage))
    out_process->cpu = cpu_usage;//std::make_unique<double>(cpu_usage);

  const int64_t network_usage = task_manager->GetCumulativeNetworkUsage(id);
  if (network_usage != -1)
    out_process->network = static_cast<double>(network_usage);//std::make_unique<double>(network_usage);

  const int64_t memory_footprint = task_manager->GetMemoryFootprintUsage(id);
  out_process->private_memory = static_cast<double>(memory_footprint);

  int64_t v8_allocated = 0;
  int64_t v8_used = 0;
  if (task_manager->GetV8Memory(id, &v8_allocated, &v8_used)) {
    out_process->js_memory_allocated = static_cast<double>(v8_allocated);
    out_process->js_memory_used = static_cast<double>(v8_used);
    //Forensics
    blink::Forensics::DebugInfo(TRACE(0), static_cast<double>(v8_allocated));
    blink::Forensics::DebugInfo(TRACE(0), static_cast<double>(v8_used));
    //
  }

  const int64_t sqlite_bytes = task_manager->GetSqliteMemoryUsed(id);
  if (sqlite_bytes != -1)
    out_process->sqlite_memory = std::make_unique<double>(sqlite_bytes);

  blink::WebCacheResourceTypeStats cache_stats;
  if (task_manager->GetWebCacheStats(id, &cache_stats)) {
    out_process->image_cache = CreateCacheData(cache_stats.images);
    out_process->script_cache = CreateCacheData(cache_stats.scripts);
    out_process->css_cache = CreateCacheData(cache_stats.css_style_sheets);
  }

  // if ( GetProcessType(task_manager->GetType(id)) == extensions::api::processes::PROCESS_TYPE_SERVICE_WORKER)
  {
      //Forensics
      TRACE(1);
      blink::Forensics::LogTaskUsageInfo(TRACE(0),process_title, out_process);
      //
  }
}

}  // namespace

////////////////////////////////////////////////////////////////////////////////
// SWProcessesForensics:
////////////////////////////////////////////////////////////////////////////////

SWProcessesForensics::SWProcessesForensics()
    : task_manager::TaskManagerObserver(base::TimeDelta::FromSeconds(1),
                                        task_manager::REFRESH_TYPE_NONE)
      
      {
        task_manager::TaskManagerInterface::GetTaskManager()->AddObserver(this);
        
}

SWProcessesForensics::~SWProcessesForensics() {
}


void SWProcessesForensics::OnTaskAdded(task_manager::TaskId id) {
  //Forensics
  TRACE(1);
  //
  Process process;
  FillProcessData(id,
                  observed_task_manager(),
                  true,  // include_optional
                  &process);
 
}

void SWProcessesForensics::OnTaskToBeRemoved(task_manager::TaskId id) {
  
  int exit_code = 0;
  base::TerminationStatus status = base::TERMINATION_STATUS_STILL_RUNNING;
  observed_task_manager()->GetTerminationStatus(id, &status, &exit_code);
 
}

void SWProcessesForensics::OnTasksRefreshedWithBackgroundCalculations(
    const task_manager::TaskIdList& task_ids) {

  // Get the data of tasks sharing the same process only once.
  std::set<base::ProcessId> seen_processes;
  base::DictionaryValue processes_dictionary;
  for (const auto& task_id : task_ids) {
    // We are not interested in tasks, but rather the processes on which they
    // run.
    const base::ProcessId proc_id =
        observed_task_manager()->GetProcessId(task_id);
    if (seen_processes.count(proc_id))
      continue;

    const int child_process_host_id =
        observed_task_manager()->GetChildProcessUniqueId(task_id);
    // Ignore tasks that don't have a valid child process host ID like ARC
    // processes. We report the browser process info here though.
    if (child_process_host_id == content::ChildProcessHost::kInvalidUniqueID)
      continue;

    seen_processes.insert(proc_id);
    Process process;
    FillProcessData(task_id,
                    observed_task_manager(),
                    true,  // include_optional
                    &process);
  }
  
}

void SWProcessesForensics::OnTaskUnresponsive(task_manager::TaskId id) {
  
  Process process;
  FillProcessData(id,
                  observed_task_manager(),
                  true,  // include_optional
                  &process);
 
}

}  // namespace sw_forensics
