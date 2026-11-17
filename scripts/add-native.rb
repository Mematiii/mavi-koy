# Adds the Game Center plugin, the custom view controller and the entitlements file to the Xcode project.
require 'xcodeproj'
project = Xcodeproj::Project.open('ios/App/App.xcodeproj')
target = project.targets.find { |t| t.name == 'App' }
group = project.main_group.children.find { |g| g.respond_to?(:path) && g.path == 'App' } || project.main_group['App']
%w[GameCenterPlugin.swift MainViewController.swift].each do |f|
  next if group.files.any? { |r| r.path == f }
  ref = group.new_reference(f)
  target.source_build_phase.add_file_reference(ref)
end
group.new_reference('App.entitlements') unless group.files.any? { |r| r.path == 'App.entitlements' }
target.build_configurations.each do |c|
  c.build_settings['CODE_SIGN_ENTITLEMENTS'] = 'App/App.entitlements'
  c.build_settings['TARGETED_DEVICE_FAMILY'] = '1'
end
project.save
puts 'native files added'
