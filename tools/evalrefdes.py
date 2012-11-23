import re

def subRefDes(template, x):
    refdes = None
    #print 'template=', template
    m = re.search('(.*)\%([A-Z0-9\/\*\+\-]+)\%(.*)', template)
    if m != None:
        try:
            X = x
            #print 'expr=', m.group(2)
            des = eval(m.group(2))
            #print 'des=', des, 'exp=', (r'\g<1>%s\g<3>' % des)
            refdes = m.expand(r'\g<1>%s\g<3>' % des)
            #print 'refdes=', refdes
        except:
            print 'Could not parse template refdes %s' % template
            exit(1)
    else:
        refdes = '%s_%s' % (template,x)
    return refdes
            
