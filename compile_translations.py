import polib

po = polib.pofile('locale/te/LC_MESSAGES/django.po')
po.save_as_mofile('locale/te/LC_MESSAGES/django.mo')
print("Telugu compiled!")

po = polib.pofile('locale/hi/LC_MESSAGES/django.po')
po.save_as_mofile('locale/hi/LC_MESSAGES/django.mo')
print("Hindi compiled!")

print("All done!")