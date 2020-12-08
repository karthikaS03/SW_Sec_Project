
'use strict';

const puppeteer = require('puppeteer');
const devices = require('puppeteer/DeviceDescriptors');
const nexus = devices['Nexus 5'];
var fs = require('fs');
// var fs_extra = require('fs-extra')

process.on('unhandledRejection', error => {
  // Prints "unhandledRejection woops!"
  console.log(site_id+' :: '+url)
	console.log('unhandledRejection', error);
});


var home_dir= '/home/pptruser/'

// function get_logs(){
//   let dirFiles = fs.readdirSync(home_dir+'app/')
//   let log_files = dirFiles.filter(function(elm){return elm.match(/vv8[0-9a-z- .]+.log/gi)}) 
//   console.log("Exporting Files Started!")
//   console.log(log_files)
//   log_files.forEach(file =>{
//       fs_extra.move(home_dir+'app/'+file, home_dir+'logs/'+file, function(err){
//           if (err) return console.error(err)
          
//       })
//   })
//   console.log("Exporting Files Completed!")
// }

async function load_page(url,id,i_count,wait_time){
  var count = 0
  
  // Viewport && Window size
  const width = 650
  const height = 1020

  

  function timer(ms){
    return new Promise(res=>setTimeout(res,ms))
  }
  
  await puppeteer.launch({ headless:false, executablePath: 
    // '/home/sk-lab/Desktop/PWA_Project_2020/project_code/chromium_pwa/src/out/Builder/chrome',
    // '../chrome_swsec/chrome',
                          home_dir+'chromium/chrome',
                          // userDataDir:home_dir+'chrome_user/',
                          // ignoreDefaultArgs: ['--enable-automation'],
                           args: [
                                '--enable-features=NetworkService',
                                '--no-sandbox',
                                // '--disable-setuid-sandbox',
                                '--window-size=${ width },${ height }',
                                '--start-maximized',
                                '--ignore-certificate-errors','--disable-gpu', '--disable-software-rasterizer', '--disable-infobars' ]
                         }).then(async browser => 
    {
        
           
        try{
                           
          

          browser.on('targetcreated', async function(target){    
        
            if(target._targetInfo.type=='page'){
              var p = await target.page()   
                          
              p.once('load',  async function(){
                try{
                    console.log('New Page Loaded @ '+new Date(Date.now()).toLocaleString())
                    const URL = require('url').URL;     
                    var current_url = p.url()       
                    url = new URL(current_url);
                    console.log('Current Url :: '+url)
                    await timer(3000)
                    await p.keyboard.down('Shift')
                    await p.keyboard.press('Escape')
                    await p.keyboard.up('Shift') 
                    
                    await timer(6000)
                    await p.addScriptTag({ url: 'https://unpkg.com/gremlins.js' });
                    console.log('Script injected @ '+new Date(Date.now()).toLocaleString())
                    await p.evaluate(() => {
                      gremlins.createHorde({
                        species: [gremlins.species.clicker(),gremlins.species.toucher(),gremlins.species.formFiller(),gremlins.species.scroller(),gremlins.species.typer()],
                        mogwais: [gremlins.mogwais.alert(),gremlins.mogwais.fps(),gremlins.mogwais.gizmo()],
                        // randomizer: new gremlins.Chance(1234),
                        strategies: [gremlins.strategies.allTogether({delay: 1000, nb: 5000 })]
                    }).unleash()
                    });
                    await setTimeout(async function() {
                      await p.reload({waitUntil:['networkidle0', 'domcontentloaded'] })
                      console.log('page reloaded')
                      try{
                        await context.overridePermissions(url.origin, ['notifications']);
                        await timer(6000)
                        const granted = await p.evaluate(async () => {
                          return (await navigator.permissions.query({name: 'notifications'})).state;
                        });
                        console.log('Granted:', granted);            
                        console.log('permission overriden')
                      }
                      catch(e){
                        console.log('Permission not overriden!!')
                        console.log(e)
                      }
                    }, 60000)
                    
                    await setTimeout(async function() {
                        console.log('Page Closed @ '+ new Date(Date.now()).toLocaleString())
                        await p.close()
                        //await browser.close()
                        // get_logs()
                    }, 300000)		           
                }
                catch(err){
                  console.log(id+" :: page load timeout")
                  console.log(err)
                  // get_logs()
                }
              })
            }
          })

          const page = await browser.newPage();          
          //await page.setViewport({ width, height })

          // Open Task Manager to record task usage
          await timer(3000)
          await page.keyboard.down('Shift')
          await page.keyboard.press('Escape')
          await page.keyboard.up('Shift')
          console.log('open task manager')
          await timer(3000)
          const context = browser.defaultBrowserContext();
          await page.setBypassCSP(true)
          
            console.log('visiting page')
            try{              
                  await page.goto(url,{waitUntil: 'load',timeout:900000});                  
              }
              catch(e){
                console.log('timeout')
              }                   
        }
        catch(error){
          //stream.write('ERROR::'+error)        
          console.log(error)
          // get_logs()
          return  
          
        
        }
        
  });
  return true
};
const timeoutPromise = (timeout) => new Promise((resolve) => setTimeout(resolve, timeout));


async function crawl_url(url, id, i_count,timeout){
      try{
        console.log('crawling started :: ' +id)
        await load_page(url,id, i_count,timeout)   
        //await timeoutPromise(timeout)        
      }
      catch(error){
        console.log(error)   
        // get_logs()     
      } 
}

if (process.argv[2]) {
  console.log('started capture screenshot')
  var url = process.argv[2];
  var site_id =process.argv[3];  
  
  // url = 'https://feedbackchoice.com'  //gauntface.github.io/simple-push-demo/'
  // site_id='12345'

  var i_count=2
  var timeout=200
  crawl_url(url,site_id,i_count,timeout)
}
